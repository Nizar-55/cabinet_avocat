from django.test import TestCase
from django.urls import reverse


class DocumentsSmokeTests(TestCase):
    def test_documents_list_view(self):
        """Ensure the documents list view is reachable (200 or redirect)."""
        url = reverse('documents:list')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200, 302))
from django.test import TestCase

# Create your tests here.
