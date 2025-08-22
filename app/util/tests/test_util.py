from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from data.models import PixMessage


class TestUtilGenerateMessages(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_generate_messages_success(self):
        ispb = "12345678"
        number = 5

        resp = self.client.post(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json().get("inserted"), number)

        qs = PixMessage.objects.filter(receiver_ispb=ispb)
        self.assertEqual(qs.count(), number)
        self.assertTrue(qs.filter(status=PixMessage.MessageStatus.PENDING).exists())

    def test_generate_messages_invalid_short_ispb(self):
        ispb = "123"
        number = 5

        resp = self.client.post(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp.json())

    def test_generate_messages_invalid_long_ispb(self):
        ispb = "123456789"
        number = 5

        resp = self.client.post(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp.json())

    def test_generate_messages_invalid_number_low(self):
        ispb = "12345678"
        number = 0

        resp = self.client.post(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp.json())

    def test_generate_messages_invalid_number_high(self):
        ispb = "12345678"
        number = 1001

        resp = self.client.post(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp.json())

    def test_generate_messages_method_get_not_allowed(self):
        ispb = "12345678"
        number = 3

        resp = self.client.get(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_generate_messages_method_put_not_allowed(self):
        ispb = "12345678"
        number = 3

        resp = self.client.put(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_generate_messages_method_delete_not_allowed(self):
        ispb = "12345678"
        number = 3

        resp = self.client.delete(f"/api/util/msgs/{ispb}/{number}")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

