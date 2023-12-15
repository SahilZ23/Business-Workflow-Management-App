from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from Syllabus_Project.models import Users, PersonalInfo  
class GeneratePayCheckTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()

    def test_generate_paycheck_view_get(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Make a GET request to the view
        response = self.client.get(reverse('/GeneratePay'))  

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the rendered template contains the expected content
        self.assertContains(response, "Generate Paycheck")

    def test_generate_paycheck_view_post(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Create a PersonalInfo instance for the test user
        personal_info = PersonalInfo.objects.create(user=self.test_user, myName='Test Employee')

        # Make a POST request to the view with necessary data
        data = {
            'user_id': personal_info.id,
            'pay_rate': '10.00',
            'hours': '40',
            'pay1': '2023-01-01',
            'pay2': '2023-01-15',
        }
        response = self.client.post(reverse('/GeneratePay'), data)  # Replace 'generate_paycheck' with the actual URL name

        # Check that the response redirects to '/HR'
        self.assertRedirects(response, '/HR', status_code=302, target_status_code=200)

