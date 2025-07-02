from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import FileUpload, ActionLog
import os
import uuid
from django.conf import settings

class FileStorageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.force_login(self.user)

    def test_file_upload_success(self):
        file_content = b'Test content for upload.'
        file = SimpleUploadedFile("test.txt", file_content)
        response = self.client.post('/storage/upload/', {'file': file})

        self.assertEqual(response.status_code, 200)
        self.assertIn('file_id', response.json())

        file_id = response.json()['file_id']
        self.assertTrue(FileUpload.objects.filter(file_id=file_id).exists())
        self.assertTrue(ActionLog.objects.filter(file_id=file_id, action='upload').exists())

    def test_upload_too_large_file(self):
        large_content = b'a' * (16 * 1024 * 1024 + 1)
        file = SimpleUploadedFile("large_file.txt", large_content)
        response = self.client.post('/storage/upload/', {'file': file})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'File too large')

    def test_upload_no_file(self):
        response = self.client.post('/storage/upload/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'No file uploaded')

    def test_download_success(self):
        # First, upload file
        content = b'Downloadable content.'
        file = SimpleUploadedFile("download.txt", content)
        upload_response = self.client.post('/storage/upload/', {'file': file})
        file_id = upload_response.json()['file_id']

        # Then, download
        response = self.client.get(f'/storage/download/{file_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, content)
        self.assertTrue(ActionLog.objects.filter(file_id=file_id, action='download').exists())

    def test_download_file_not_found(self):
        fake_id = str(uuid.uuid4())
        response = self.client.get(f'/storage/download/{fake_id}/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'File not found')

    def tearDown(self):
        # Clean up media files
        for file in FileUpload.objects.all():
            chunk_dir = os.path.join(settings.MEDIA_ROOT, file.file_id)
            if os.path.exists(chunk_dir):
                for f in os.listdir(chunk_dir):
                    os.remove(os.path.join(chunk_dir, f))
                os.rmdir(chunk_dir)
        FileUpload.objects.all().delete()
        ActionLog.objects.all().delete()
        self.user.delete()

