from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "medicine-upload-tests",
        }
    }
)
class ImageUploadViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_dir = TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls._media_dir.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="upload-user",
            password="pass12345",
            email="upload@example.com",
            phone="13800000001",
        )
        self.client.force_authenticate(user=self.user)

    def test_upload_image_succeeds_when_image_library_unavailable(self):
        upload_file = SimpleUploadedFile(
            "medicine.png",
            (
                b"\x89PNG\r\n\x1a\n"
                b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT"
                b"\x08\x99c`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00"
                b"\x00\x00IEND\xaeB`\x82"
            ),
            content_type="image/png",
        )

        with patch(
            "apps.medicines.upload_views._load_image_module",
            side_effect=ImportError("Pillow unavailable"),
        ):
            with self.settings(MEDIA_ROOT=self._media_dir.name):
                response = self.client.post(
                    "/api/medicines/upload-image/",
                    {"image": upload_file},
                    format="multipart",
                )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("image_path", payload["data"])
        saved_path = Path(self._media_dir.name) / payload["data"]["image_path"]
        self.assertTrue(saved_path.exists())

    def test_upload_image_requires_authentication(self):
        self.client.force_authenticate(user=None)
        upload_file = SimpleUploadedFile(
            "medicine.png",
            b"file-content",
            content_type="image/png",
        )

        with self.settings(MEDIA_ROOT=self._media_dir.name):
            response = self.client.post(
                "/api/medicines/upload-image/",
                {"image": upload_file},
                format="multipart",
            )

        self.assertEqual(response.status_code, 401)

    def test_upload_image_accepts_heic_content_type(self):
        upload_file = SimpleUploadedFile(
            "iphone.heic",
            b"heic-content",
            content_type="image/heic",
        )

        with self.settings(MEDIA_ROOT=self._media_dir.name):
            response = self.client.post(
                "/api/medicines/upload-image/",
                {"image": upload_file},
                format="multipart",
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("image_path", payload["data"])
