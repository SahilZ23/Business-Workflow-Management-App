from Syllabus_Project.models import Users,PersonalInfo, Customer, ROLES, Orders, Items, Orders, OrderItems
from django.forms.models import modelformset_factory
import re
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages

class Validations():
    def checkLogin(self, request):
        if not request.session.get("user_username"):
            return False
        return True

    def checkRole(self, request, *roles):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        for role in roles:
            if user.role == role:
                return True
        return False

    def checkPersonalInfoPost(self, name, officeLocation, officeNumber, phoneNumber, email):
        is_aplpha = re.compile('[A-Za-z]')
        is_email_reg = re.compile('^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]\w+[.]\w{2,3}$')
        is_num = re.compile('^\d{3,5}$')
        is_phone_reg = re.compile('^\d{3}-\d{3}-\d{4}|\d{3}\d{3}\d{4}$')
        errors = []
        parse_fail = False

        if not is_aplpha.match(name):
            errors.append("Name should not include numbers or any characters")

        if not is_aplpha.match(officeLocation):
            errors.append("Office Location is invalid")

        if not is_email_reg.match(email):
            errors.append("email is invalid")

        if not is_phone_reg.match(phoneNumber):
            errors.append("Invalid Phone Number")

        if not is_num.match(officeNumber):
            errors.append("Office Number should be an Integer and be between 3 to 5 numbers")
            parse_fail = True

        if not parse_fail:
            try:
                office_num = int(officeNumber)

                if office_num <= 0:
                    errors.append("Office Number must be a positive integer")

            except(ValueError, TypeError):
                errors.append("Error: Could not parse numeric input")
        return errors

    def checkAddUserPost(self, fullname, username, password, role, region):
        is_numeric_regex = re.compile('[\d]+')
        has_alphanum_regex = re.compile('^[_.\-A-Za-z\d]+$')
        errors = []

        if is_numeric_regex.match(fullname):
            errors.append("Name cannot have numbers")

        if not has_alphanum_regex.match(username):
            errors.append("Username must be only letters or numbers or -._")

        if (role,role) not in ROLES:
            errors.append("Role not a valid role")


        if role == 'SalesRep' and not region:
            errors.append("Region is required for Sales Representatives.")

        if role != 'SalesRep' and region:
            errors.append("Region should only be set for Sales Representatives.")
        
        if role=="SalesRep" and is_numeric_regex.match(region):
            errors.append("Region cannot have numbers")

        # password requirements
        if len(password) == 0:
            errors.append("Password is required")
        elif len(password) == 1:
            errors.append("Password is weak")

        return errors

    def check_order_num_unique(self, order_num):
            errors = []
            if Orders.objects.filter(orderNum=order_num).exists():
                errors.append("Order number must be unique.")
            return errors
    

class PasswordResetViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = Users.objects.create(user_username='testuser', user_password='old_password', role='Admin')
        self.client = Client()
        self.client.force_login(self.user)  # Log in the user for testing

    def test_password_reset_get(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'passwordReset.html')

    def test_password_reset_post_success(self):
        data = {
            'new_password': 'new_password',
            'confirm_password': 'new_password'
        }
        response = self.client.post(reverse('password_reset'), data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.user_password, 'new_password')
        self.assertRedirects(response, reverse('adminPage'))  # Replace 'adminPage' with the correct URL name

    def test_password_reset_post_non_matching_passwords(self):
        data = {
            'new_password': 'new_password',
            'confirm_password': 'different_password'
        }
        response = self.client.post(reverse('password_reset'), data)
        self.assertIn('Passwords do not match', response.context['message'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'passwordReset.html')

class AddUserViewTest(TestCase):

    def setUp(self):
        self.admin_user = Users.objects.create(user_username='admin', user_password='adminpass', role='Admin')
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_add_user_get_as_admin(self):
        response = self.client.get(reverse('add_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'adduser.html')

    def test_add_user_post_success(self):
        data = {
            'fullname': 'Test User',
            'username': 'testuser',
            'password': 'password',
            'role': 'SalesRep',
            'phone': '1234567890'
        }
        response = self.client.post(reverse('add_user'), data)
        self.assertEqual(Users.objects.count(), 2)
        self.assertTrue(Users.objects.filter(user_username='testuser').exists())
        self.assertRedirects(response, reverse('admin_page'))  # Replace 'admin_page' with the correct URL name

    def test_add_user_post_invalid_data(self):
        data = {
            'fullname': '',
            'username': '',
            'password': '',
            'role': '',
            'phone': ''
        }
        response = self.client.post(reverse('add_user'), data)
        self.assertIn('message', response.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'adduser.html')

class DeleteUsersViewTest(TestCase):

    def setUp(self):
        self.admin_user = Users.objects.create(user_username='admin', user_password='adminpass', role='Admin')
        self.user_to_delete = Users.objects.create(user_username='testuser', user_password='testpass', role='HR')
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_delete_users_get(self):
        response = self.client.get(reverse('delete_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'deleteUsers.html')
        self.assertIn(self.user_to_delete, response.context['users'])

    def test_delete_users_post(self):
        response = self.client.post(reverse('delete_users'), {'User': self.user_to_delete.id})
        self.assertEqual(Users.objects.count(), 1)
        self.assertFalse(Users.objects.filter(id=self.user_to_delete.id).exists())
        self.assertRedirects(response, reverse('admin_page'))  # Replace 'admin_page' with the correct URL name


class DeleteCustomerViewTest(TestCase):

    def setUp(self):
        self.admin_user = Users.objects.create(user_username='admin', user_password='adminpass', role='Admin')
        personal_info = PersonalInfo.objects.create(myName='John Doe', phoneNumber='1234567890')
        self.customer_to_delete = Customer.objects.create(
            cusFirstName='John',
            CusLastName='Doe',
            user=self.admin_user,
            cusAddress='123 Main St',
            phoneNumber='1234567890',
            email='john.doe@example.com'
        )
        self.admin_user.info = personal_info
        self.admin_user.save()
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_delete_customer_get(self):
        response = self.client.get(reverse('delete_customer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'deleteCustomer.html')
        self.assertIn(self.customer_to_delete, response.context['customers'])

    def test_delete_customer_post(self):
        response = self.client.post(reverse('delete_customer'), {'Customer': self.customer_to_delete.id})
        self.assertEqual(Customer.objects.count(), 0)
        self.assertFalse(Customer.objects.filter(id=self.customer_to_delete.id).exists())
        self.assertRedirects(response, reverse('admin_page'))  # Replace 'admin_page' with the correct URL name

class AddCustomerViewTest(TestCase):

    def setUp(self):
        # Creating test user with appropriate role
        self.test_user = Users.objects.create(user_username='testuser', user_password='password', role='SalesRep')
        self.client = Client()
        self.client.force_login(self.test_user)

    def test_add_customer_get_as_authorized_user(self):
        response = self.client.get(reverse('add_customer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addCustomer.html')

    def test_add_customer_post_success(self):
        data = {
            'cusFirstName': 'John',
            'cusLastName': 'Doe',
            'cusAddress': '123 Main St',
            'cusCity': 'Cityville',
            'cusState': 'Stateville',
            'cusZip': '12345',
            'phoneNumber': '1234567890',
            'email': 'john.doe@example.com'
        }
        response = self.client.post(reverse('add_customer'), data)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertTrue(Customer.objects.filter(cusFirstName='John').exists())
        self.assertRedirects(response, reverse('admin_page'))  # Replace 'admin_page' with the correct URL name

    def test_add_customer_post_invalid_data(self):
        data = {
            'cusFirstName': '',
            'cusLastName': '',
            # other fields omitted for brevity
        }
        response = self.client.post(reverse('add_customer'), data)
        self.assertIn('message', response.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addCustomer.html')

class AddOrderViewTest(TestCase):

    def setUp(self):
        self.user = Users.objects.create(user_username='testuser', user_password='password', role='Admin')
        Customer.objects.create(...)  # Add required fields
        Items.objects.create(...)  # Add required fields
        self.client = Client()
        self.client.force_login(self.user)

    def test_add_order_get_as_authorized_user(self):
        response = self.client.get(reverse('add_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addOrder.html')
        self.assertIsInstance(response.context['formset'], modelformset_factory(OrderItems, form=OrderItemsForm))

    def test_add_order_post_success(self):
        data = {
            'orderNum': 123,
            'Customer': customer_id,  # Use an actual customer id
            'orderDate': '2023-01-01',
            # Add other fields and formset data as required
        }
        response = self.client.post(reverse('add_order'), data)
        self.assertEqual(Orders.objects.count(), 1)
        self.assertTrue(Orders.objects.filter(orderNum=123).exists())
        # Check redirection based on user role

