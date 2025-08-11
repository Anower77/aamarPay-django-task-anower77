import io
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from core.models import PaymentTransaction


class MyEndpointsTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Create a successful payment so upload passes
        PaymentTransaction.objects.create(
            user=self.user,
            transaction_id="test-tx",
            amount=100,
            status="success",
            gateway_response={}
        )
        
    @patch('core.views.process_file_task.delay')
    def test_file_upload(self, mock_celery_task):
        file_content = io.BytesIO(b"Sample file content")
        file_content.name = "sample.txt"
        response = self.client.post(reverse('file-upload'), {'file': file_content})
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 201)
        
        # Verify Celery task was called
        mock_celery_task.assert_called_once()
        
    def test_file_list(self):
        response = self.client.get(reverse('file-list'))
        self.assertEqual(response.status_code, 200)
        
    def test_transaction_list(self):
        response = self.client.get(reverse('transaction-list'))
        self.assertEqual(response.status_code, 200)

    def test_activity_list(self):
        response = self.client.get(reverse('activity-list'))
        self.assertEqual(response.status_code, 200)
