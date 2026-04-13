from django.test import TestCase, override_settings
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.test import APIClient


@api_view(["GET"])
@permission_classes([AllowAny])
def request_id_ok_view(request):
    return Response({"success": True, "data": {"ok": True}})


@api_view(["POST"])
@permission_classes([AllowAny])
def request_id_error_view(request):
    raise ValidationError({"field": ["必填"]})


urlpatterns = [
    path("api/test-request-id/ok/", request_id_ok_view),
    path("api/test-request-id/error/", request_id_error_view),
]


@override_settings(
    ROOT_URLCONF=__name__,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "request-id-tests",
        }
    },
)
class RequestIdIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_echoes_request_id_header_on_success_response(self):
        response = self.client.get(
            "/api/test-request-id/ok/", HTTP_X_REQUEST_ID="req-success-123"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Request-ID"], "req-success-123")
        self.assertEqual(response.json()["data"]["ok"], True)

    def test_returns_request_id_in_validation_error_response(self):
        response = self.client.post(
            "/api/test-request-id/error/",
            data={},
            format="json",
            HTTP_X_REQUEST_ID="req-error-456",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["X-Request-ID"], "req-error-456")
        payload = response.json()
        self.assertEqual(payload["request_id"], "req-error-456")
        self.assertEqual(payload["error_code"], "VALIDATION_ERROR")
        self.assertIn("field", payload["data"])

    def test_generates_request_id_when_header_missing(self):
        response = self.client.get("/api/test-request-id/ok/")

        self.assertEqual(response.status_code, 200)
        generated_request_id = response["X-Request-ID"]
        self.assertTrue(generated_request_id)
        self.assertGreaterEqual(len(generated_request_id), 8)
