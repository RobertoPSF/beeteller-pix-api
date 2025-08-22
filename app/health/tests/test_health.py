from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class TestHealth(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_health_returns_ok(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), {"message": "ok"})

    def test_post_health_not_allowed(self):
        resp = self.client.post("/health", data={})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_health_not_allowed(self):
        resp = self.client.delete("/health", data={})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_health_not_allowed(self):
        resp = self.client.put("/health", data={})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

