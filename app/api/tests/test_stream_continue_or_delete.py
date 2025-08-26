from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from data.models import PixMessage, PixStream


class TestStreamContinueAndDelete(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.ispb = "12345678"


    def _create_message(self, suffix: str = "1") -> PixMessage:
        return PixMessage.objects.create(
            end_to_end_id=f"E{self.ispb}{suffix}",
            tx_id=f"tx{suffix}",
            amount=Decimal("10.00"),
            payment_at=timezone.now(),
            free_text="",
            payer_name="Tester",
            payer_cpf_cnpj="12345678901",
            payer_ispb="87654321",
            payer_agencia="0001",
            payer_conta_transacional="111",
            payer_tipo_conta="CACC",
            receiver_name="Receiver",
            receiver_cpf_cnpj="01987654321",
            receiver_ispb=self.ispb,
            receiver_agencia="0001",
            receiver_conta_transacional="222",
            receiver_tipo_conta="SVGS",
        )


    def _create_stream(self, interation_id: str = "s1", active: bool = True) -> PixStream:
        return PixStream.objects.create(interation_id=interation_id, ispb=self.ispb, active=active)


    def test_invalid_ispb_returns_400(self):
        stream = self._create_stream("test")
        resp = self.client.get(f"/api/pix/123/stream/{stream.interation_id}")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp.json())


    def test_stream_not_found_returns_404(self):
        resp = self.client.get(f"/api/pix/{self.ispb}/stream/doesnotexist")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", resp.json())


    def test_closed_stream_returns_410(self):
        stream = self._create_stream("test", active=False)
        resp = self.client.get(f"/api/pix/{self.ispb}/stream/{stream.interation_id}")
        self.assertEqual(resp.status_code, status.HTTP_410_GONE)
        self.assertIn("detail", resp.json())


    def test_unsupported_accept_returns_406(self):
        stream = self._create_stream("test")
        resp = self.client.get(
            f"/api/pix/{self.ispb}/stream/{stream.interation_id}", HTTP_ACCEPT="text/plain"
        )
        self.assertEqual(resp.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertIn("detail", resp.json())


    def test_get_continuation_reserves_single_message(self):
        stream = self._create_stream("test")
        msg = self._create_message("m1")
        resp = self.client.get(
            f"/api/pix/{self.ispb}/stream/{stream.interation_id}", HTTP_ACCEPT="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        body = resp.json()
        self.assertIsInstance(body, dict)
        self.assertEqual(body["endToEndId"], msg.end_to_end_id)

        msg.refresh_from_db()
        self.assertEqual(msg.status, PixMessage.MessageStatus.RESERVED)
        self.assertEqual(msg.reserved_by_id, stream.id)


    def test_get_continuation_multipart_reserves_up_to_10(self):
        stream = self._create_stream("test")
        for i in range(12):
            self._create_message(f"mm{i}")
        resp = self.client.get(
            f"/api/pix/{self.ispb}/stream/{stream.interation_id}", HTTP_ACCEPT="multipart/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        body = resp.json()
        self.assertIsInstance(body, list)
        self.assertLessEqual(len(body), 10)

        reserved_count = PixMessage.objects.filter(reserved_by=stream).count()
        self.assertEqual(reserved_count, len(body))


    def test_delete_consumes_and_closes_stream(self):
        stream = self._create_stream("test")
        self._create_message("del1")

        resp_get = self.client.get(
            f"/api/pix/{self.ispb}/stream/{stream.interation_id}", HTTP_ACCEPT="application/json"
        )
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

        resp_del = self.client.delete(f"/api/pix/{self.ispb}/stream/{stream.interation_id}")
        self.assertEqual(resp_del.status_code, status.HTTP_200_OK)

        stream.refresh_from_db()
        self.assertFalse(stream.active)
        
        consumed = PixMessage.objects.filter(reserved_by=stream, status=PixMessage.MessageStatus.CONSUMED)
        self.assertTrue(consumed.exists())


    def test_put_stream_continue_not_allowed(self):
        resp = self.client.put(f"/api/pix/{self.ispb}/stream/test")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_post_stream_continue_not_allowed(self):
        resp = self.client.post(f"/api/pix/{self.ispb}/stream/test")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_no_messages_returns_204_with_pull_next(self):
        stream = self._create_stream("s204")
        resp = self.client.get(
            f"/api/pix/{self.ispb}/stream/{stream.interation_id}", HTTP_ACCEPT="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("Pull-Next", resp)


    def test_parallel_streams_continuation_do_not_duplicate_messages(self):
        self._create_message("p1")
        self._create_message("p2")
        
        s1 = self._create_stream("ps1")
        s2 = self._create_stream("ps2")

        r1 = self.client.get(
            f"/api/pix/{self.ispb}/stream/{s1.interation_id}", HTTP_ACCEPT="application/json"
        )
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        id1 = r1.json()["endToEndId"]

        r2 = self.client.get(
            f"/api/pix/{self.ispb}/stream/{s2.interation_id}", HTTP_ACCEPT="application/json"
        )
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        id2 = r2.json()["endToEndId"]

        self.assertNotEqual(id1, id2)