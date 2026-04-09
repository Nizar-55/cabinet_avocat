from django.test import TestCase
from django.urls import reverse


class ClientsSmokeTests(TestCase):
    def test_clients_list_view(self):
        """Ensure the clients list view is reachable (200 or redirect)."""
        url = reverse('clients:list')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200, 302))
from django.test import TestCase

# Create your tests here.
