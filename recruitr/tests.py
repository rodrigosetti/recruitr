from django.test import TestCase, Client

# Create your tests here.
class RecruiterTestCase(TestCase):
    """Test cases for RecruiterTestCase."""
    def setUp(self):
        self.client = Client()

    def test_index_rendering(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome', str(response.content), 'Welcome in the page.')
