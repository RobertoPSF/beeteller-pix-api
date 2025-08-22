from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from data.models import PixMessage, PixStream


class TestStreamStart(TestCase):
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


    def test_invalid_ispb_returns_400(self):
        resp = self.client.get("/api/pix/123/stream/start")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp.json())


    def test_unsupported_accept_returns_406(self):
        resp = self.client.get(f"/api/pix/{self.ispb}/stream/start", HTTP_ACCEPT="text/plain")
        self.assertEqual(resp.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertIn("detail", resp.json())


    def test_limit_6_active_streams_returns_429(self):
        PixStream.objects.bulk_create([
            PixStream(interation_id=f"s{i}", ispb=self.ispb, active=True) for i in range(6)
        ])
        resp = self.client.get(f"/api/pix/{self.ispb}/stream/start")
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


    def test_application_json_returns_single_message(self):
        self._create_message("test")
        resp = self.client.get(f"/api/pix/{self.ispb}/stream/start", HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("Pull-Next", resp)

        body = resp.json()
        self.assertIsInstance(body, dict)
        self.assertIn("endToEndId", body)

        msg = PixMessage.objects.get(end_to_end_id=body["endToEndId"])
        self.assertEqual(msg.status, PixMessage.MessageStatus.RESERVED)
        self.assertIsNotNone(msg.reserved_by)


    def test_multipart_json_returns_list_up_to_10(self):
        for i in range(15):
            self._create_message(str(i))
        
        resp = self.client.get(f"/api/pix/{self.ispb}/stream/start", HTTP_ACCEPT="multipart/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("Pull-Next", resp)

        body = resp.json()
        self.assertIsInstance(body, list)

        self.assertLessEqual(len(body), 10)

