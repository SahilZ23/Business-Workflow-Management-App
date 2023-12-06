from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from Syllabus_Project.models import Users, Courses, PersonalInfo, Section, Policies, Customer, Orders, Items, OrderItems, Employee
from Syllabus_Project.Validations import Validations
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.db import transaction
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from project import settings
import urllib.parse
import requests
from django import forms
from sinch import Client

validate = Validations()


# Create your views here.

# LOGIN AND VERIFICATION

class Login(View):
    def get(self, request):
        # request.session.pop("user_username", None)
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("loginEmail")
        password = request.POST.get("loginPassword")
        message = ""
        users = list(Users.objects.filter(user_username=username))
        if len(users) != 0:
            u = users[0]
            if u.user_password == password:
                try:
                    # The key from one of your Verification Apps, found here https://dashboard.sinch.com/verification/apps
                    applicationKey = "554cffac-3633-4a76-aafd-8dec9c294b2a"

                    # The secret from the Verification App that uses the key above, found here https://dashboard.sinch.com/verification/apps
                    applicationSecret = "ZDotwc7m30WkVkyjYL284w=="

                    # The number that will receive the SMS. Test accounts are limited to verified numbers.
                    # The number must be in E.164 Format, e.g. Netherlands 0639111222 -> +31639111222
                    phone = "+1" + u.info.phoneNumber
                    toNumber = phone

                    sinchVerificationUrl = "https://verification.api.sinch.com/verification/v1/verifications"

                    payload = {
                        "identity": {
                            "type": "number",
                            "endpoint": toNumber
                        },
                        "method": "sms"
                    }

                    headers = {"Content-Type": "application/json"}

                    response = requests.post(sinchVerificationUrl, json=payload, headers=headers, auth=(applicationKey, applicationSecret))

                    data = response.json()
                except Exception as ex:
                    print("Exception occurred:", ex, data['status'])
                if u.role == "Admin":
                    request.session["user_username"] = username
                    return redirect("/Verify")
                if u.role == "SalesAdmin":
                    request.session["user_username"] = username 
                    return redirect("/Verify")          
                if u.role == "Operations":
                    request.session["user_username"] = username
                    return redirect("/Verify")
                if u.role == "SalesRep":
                    request.session["user_username"] = username
                    return redirect("/Verify")
                if u.role == "HR":
                    request.session["user_username"] = username
                    return redirect("/Verify")
                if u.role == "cus":
                    request.session["user_username"] = username
                    return redirect("/Verify")
            else:
                message = "Invalid Username/Password"
        else:
            message = "Invalid Username/Password"
        return render(request, "login.html", {"message": message})

class verify(View):
    def get(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        return render(request, "verify.html", {"user": user})
    def post(self, request):
        u = Users.objects.get(user_username=request.session.get("user_username"))
        message = ""
        # The code which was sent to the number.
        code = request.POST['code']

        # The key from one of your Verification Apps, found here https://dashboard.sinch.com/verification/apps
        applicationKey = "554cffac-3633-4a76-aafd-8dec9c294b2a"

        # The secret from the Verification App that uses the key above, found here https://dashboard.sinch.com/verification/apps
        applicationSecret = "ZDotwc7m30WkVkyjYL284w=="

        # The number to which the code was sent. Test accounts are limited to verified numbers.
        # The number must be in E.164 Format, e.g. Netherlands 0639111222 -> +31639111222
        # toNumber = '+14148823039'
        phone = "+1" + u.info.phoneNumber
        toNumber = phone

        sinchVerificationUrl = "https://verification.api.sinch.com/verification/v1/verifications/number/" + toNumber

        payload = {
            "method": "sms",
            "sms": {
                "code": code
            }
        }

        headers = {"Content-Type": "application/json"}

        response = requests.put(sinchVerificationUrl, json=payload, headers=headers, auth=(applicationKey, applicationSecret))

        data = response.json()
        if data.get('status') == 'SUCCESSFUL':
            status = data['status']
            if status == 'SUCCESSFUL':
                if u.role == "Admin":
                    return redirect("adminPage")
                if u.role == "SalesAdmin":
                    return redirect("SalesAdmin")            
                if u.role == "Operations":
                    return redirect("Operations")
                if u.role == "SalesRep":
                    return redirect("salesRep")
                if u.role == "HR":
                    return redirect("HR")
                if u.role == "cus":
                    return redirect("customer")
        else:
            error_message = data.get('message', 'Verification Failed. Please try again.')
            return render(request, "verify.html", {"message": error_message, "user": u})

# PASSWORD RESET

class PasswordReset(View):
    def get(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        role = user.role
        return render(request, "passwordReset.html", {"role": role})

    def post(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            return render(request, "passwordReset.html", {"message": "Passwords do not match"})

        try:
            user.user_password = new_password
            user.save()
            messages.success(request, "Password successfully updated.")
        except Users.DoesNotExist:
            messages.error(request, "User not found.")

        # Redirect based on user role

        if user.role == "Admin":
            return redirect("adminPage")
        if user.role == "SalesAdmin":
            return redirect("SalesAdmin")            
        if user.role == "Operations":
            return redirect("Operations")
        if user.role == "SalesRep":
            return redirect("salesRep")
        if user.role == "HR":
            return redirect("HR")
        if user.role == "cus":
            return redirect("customer")

# USER ADD/DELETE

class AddUser(View):
    def get(self, request):
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
        except Exception as ex:
            print("Exception:", ex)
            return redirect("login")
        
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        return render(request, "adduser.html", {"user": user})

    def post(self, request):
        fullname = None
        username = None
        password = None
        role = None
        region = None

        try:
            fullname = request.POST['fullname']
            username = request.POST['username']
            password = request.POST['password']
            role = request.POST['role']
            phone = request.POST['phone']

            # validation
            errors = validate.checkAddUserPost(fullname, username, password, role, region)
            if len(errors) > 0:
                error_msg = 'Please correct the following: '
                for error in errors:
                    error_msg += error + '. '
                return render(request, "adduser.html", {"message": error_msg})

        except Exception as ex:
            print("Exception: ", ex)
            return render(request, "adduser.html", {"message": 'Something went wrong, check your information.'})

        if Users.objects.filter(user_username=username).exists():
            user = Users.objects.get(user_username=username)
            user.user_username = username
            user.user_password = password
            user.role = role
            user.region = region
            

            # store personal information
            if user.info is None:
                user.info = PersonalInfo.objects.create(myName=fullname, phoneNumber=phone)
            else:
                user.info.myName = fullname
                user.info.phoneNumber = phone
                user.info.save()

            user.save()
        else:
            new_personal_info = PersonalInfo.objects.create(myName=fullname, phoneNumber=phone)
            newUser = Users.objects.create(user_username=username, user_password=password, role=role,
                                           info=new_personal_info, region=region)
            newUser.save()

        return Admin.get(self, request)

class DeleteUsers(View):
    def get(self, request):
        users = list(Users.objects.exclude(role="SalesRep"))
        return render(request, "deleteUsers.html", {"users": users})

    def post(self, request):
        user = Users.objects.get(id=request.POST['User'])
        if hasattr(user, 'info'):  
            user.info.delete()     
        user.delete()    
        return redirect('/adminPage')

# PERSONAL INFO

class AddPersonalInfo(View):
    def get(self, request, user_id):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "HR"):
            return redirect("login")

        # make sure the request is for a valid user that exists
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            role = user.role
        except Exception as ex:
            return redirect("login")

        return render(request, "personalInfo.html", {"user": user, "role": role, "user_id": user_id})

    def post(self, request):
        pi = None
        name = None
        add = None
        p_num = None
        email = None
        try:
            name = request.POST.get('name')
            add = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip = request.POST.get('zip')
            p_num = request.POST.get('PhoneNumber')
            email = request.POST.get('email')

            # validation
            # errors = validate.checkPersonalInfoPost(name=name, phoneNumber=p_num, email=email)
            # if len(errors) > 0:
            #     error_msg = 'Please correct the following: '
            #     for error in errors:
            #         error_msg += error + '. '
            #     return render(request, "personalInfo.html", {"message": error_msg})

        except Exception as ex:
            return render(request, "personalInfo.html", {"message": 'Something went wrong, check your information.'})

        pi, created = PersonalInfo.objects.get_or_create(
            myName=name,
            defaults={'address': add, 'phoneNumber': p_num, 'email': email}
        )
        if not created:
            # If PersonalInfo already exists, update it
            PersonalInfo.objects.filter(id=pi.id).update(myName=name, address=add, city=city, state=state, zip=zip, phoneNumber=p_num, email=email)

        return redirect('/HR')

#CUSTOMER ADD/EDIT + DELETE

class AddCustomer(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or Validations.checkRole(self, request, "HR", "Operations", "SalesRep"):
            return redirect("login")

        # Make sure the login request is from a valid user.
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            role = user.role
        except Exception as ex:
            return redirect("login")

        # render the create customer form
        return render(request, "addCustomer.html", {"user": user, "role": role})  

    def post(self, request):
        # Retrieve and validate customer data from the POST request
        user = Users.objects.get(user_username=request.session.get("user_username"))
        cusFirstName = request.POST.get('cusFirstName')
        cusLastName = request.POST.get('cusLastName')
        cusAddress = request.POST.get('cusAddress')
        cusCity = request.POST.get('cusCity')
        cusState = request.POST.get('cusState')
        cusZip = request.POST.get('cusZip')
        phoneNumber = request.POST.get('phoneNumber')
        email = request.POST.get('email')
        
        
        
        # Perform validation using your validation module (if needed)
        # Example: errors = validate.checkCustomerInfoPost(cusName, cusAddress, phoneNumber, email)
        # Check for validation errors
        # Example: if len(errors) > 0:
        #     error_msg = 'Please correct the following: '
        #     for error in errors:
        #         error_msg += error + '. '
        #     return render(request, "customer_form.html", {"message": error_msg})

        try:
            # Generate username and password
            username = cusFirstName[0].lower() + cusLastName.lower()
            password = cusLastName[0].lower() + phoneNumber
            with transaction.atomic():
                # Create a new Users instance with the role "Customer"
                user_role = "cus"
                cus_user = Users.objects.create(
                    user_username=username,
                    user_password=password,
                    role=user_role
                )

                # Create a new Customer instance and save it to the database
                customer = Customer(cusFirstName=cusFirstName, CusLastName=cusLastName,
                                    user = cus_user,
                                    cusAddress=cusAddress, cusCity=cusCity, cusState=cusState, 
                                    cusZip=cusZip, phoneNumber=phoneNumber, email=email)
                customer.save()

            # Send Email about account creation
            try: 
                subject = "Welcome to Our Service"
                context = {
                    'customer_name': customer.cusFirstName, 
                    'customer_username': username,  # Assuming username variable holds the username
                    'customer_password': password,  # Assuming password variable holds the password
                }
                html_content = render_to_string('customerWelcome.html', context)
                text_content = strip_tags(html_content)  # Fallback for plain text email clients
                                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[str(customer.email)]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

            except Exception as ex:
                print("Email sending failed: ", ex)

            print(customer.id)
            if user.role == "Admin":
                return redirect('/adminPage')
            if user.role == "SalesAdmin":
                return redirect('/SalesAdminView')
            elif user.role == "SalesRep":
                return redirect("salesRep")
            
        except Exception as ex:
            print(ex)
            return render(request, "addCustomer.html", {"message": 'Something went wrong, check your information.'})
        
class DeleteCustomer(View):
    def get(self, request):
        customers = list(Customer.objects.all())
        return render(request, "deleteCustomer.html", {"customers": customers})

    def post(self, request):
        customer_id = request.POST.get('Customer')
        Customer.objects.get(id=customer_id).delete()
        return redirect('/adminPage')

# ORDER ADD/EDIT + DELETE + VIEW + PROCESS

class AddOrder(View):
    def get(self, request):
        # if not Validations.checkLogin(request) or Validations.checkRole(request, ["Admin", "SalesRep", "SalesAdmin", "Operations"]):
        #     return redirect("login")
        
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            customers = Customer.objects.all()
            OrderItemFormset = modelformset_factory(OrderItems, form=OrderItemsForm, extra=3)
            formset = OrderItemFormset(queryset=OrderItems.objects.none())

        except Exception as ex:
            return redirect("login")
        
        return render(request, "addOrder.html", {"user": user, "customers": customers, "formset": formset})

    def post(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        OrderItemFormset = modelformset_factory(OrderItems, form=OrderItemsForm, extra=3)
        formset = OrderItemFormset(request.POST)
        order_amount = 0
        
        if formset.is_valid():
            with transaction.atomic():
                try:
                    order_num = request.POST.get('orderNum')
                    customer = Customer.objects.get(id=request.POST.get('Customer'))
                    order_date = request.POST.get('orderDate')
                    
                    # Check if order number is unique
                    print(order_num)
                    errors = validate.check_order_num_unique(order_num)
                    if errors:
                        error_msg = ' '.join(errors)  # Join the list of errors into a single string message
                        formset = OrderItemFormset(request.POST)  # Reinitialize formset with posted data
                        return render(request, "addOrder.html", {
                            "message": error_msg,
                            "user": user,
                            "customers": Customer.objects.all(),
                            "formset": formset
                        })
                
                
                    # Create a new order instance without saving to the database yet
                    order = Orders(orderNum=order_num, Customer=customer, orderDate=order_date, orderAmount=0)

                    
                    # Temporarily save the order to associate it with order items
                    order.save()
                    order_items = []
                    # Create order items and calculate the total amount
                    for form in formset.cleaned_data:
                        if form:
                            item = form['item']
                            quantity = form['quantity']
                            if item and quantity:
                                order_item = OrderItems(order=order, item=item, quantity=quantity)
                                item_price = item.ItemPrice
                                order_amount += item_price * quantity
                                order_item.save()
                                order_items.append(order_item)

                    order.orderAmount = order_amount
                    order.save()

                    # Send Text Message
                    sinch_client = Client(
                        key_id="68db7cad-c377-4a64-a223-ad2a534ee18c",
                        key_secret="PJBGjR6Gno-3rWl-t_OSIPFub~",
                        project_id="26137e24-6715-4df3-936c-7005ff1c9945"
                    )

                    phone = "1"+ str(customer.phoneNumber)
                    sinch_client.sms.batches.send(
                        body="Hello from BWMSoln! Your Order has been successfully placed. The Total ammount is " + str(order_amount) + "." 
                        "You will receive a notification when your order has been processed. Thank you for shopping with us!",
                        to=[phone],
                        from_="12085810216",
                        delivery_report="none"
                    )
                    
                    # Send Email
                    try: 
                        subject = "Order Confirmation"
                        name = customer.cusFirstName + " " + customer.CusLastName
                        context = {
                            'customer_name': name, 
                            'order_items': order_items,
                            'total_amount': order_amount,
                        }
                        html_content = render_to_string('orderConfirmation.html', context)
                        text_content = strip_tags(html_content)  # Fallback for plain text email clients
                        
                        email = EmailMultiAlternatives(
                            subject=subject,
                            body=text_content,
                            from_email=settings.EMAIL_HOST_USER,
                            to=[str(customer.email)]
                        )
                        email.attach_alternative(html_content, "text/html")
                        email.send()

                    except Exception as ex:
                        print("Email sending failed: ", ex)

                    if user.role == "Admin":
                        return redirect('/adminPage')
                    elif user.role == "Operations":
                        return redirect('/Operations')
                    elif user.role == "SalesRep":
                        return redirect("/salesRep")

                except Exception as ex:
                    print("Exception:", ex)
                    return render(request, "addOrder.html")
        else:
            # If formset is not valid, re-render the page with existing form data
            return render(request, "addOrder.html", {
                "user": user,
                "customers": Customer.objects.all(),
                "formset": formset
            })
        
class ViewOrders(View):
    def get(self, request, order_id=None):
        # Check if an order_id is provided
        if order_id:
            return self.view_specific_order(request, order_id)
        
        # Authentication and role checks
        user = Users.objects.get(user_username=request.session.get("user_username"))
        if user.role not in ["Admin", "Operations", "SalesAdmin", "SalesRep"]:
            return redirect("login")

        if user.role== "SalesRep":
            customers = Customer.objects.filter(cusCity=user.region)
            order = Orders.objects.all()
            orders = []

            for i in order:
                if i.Customer in customers:
                    orders.append(i)
        else:
            # Fetch all orders
            orders = Orders.objects.all()

        # Render the view orders template
        return render(request, "viewOrders.html", {"orders": orders, "user": user})
    
    def view_specific_order(self, request, order_id):
        # Authentication and role checks
        user = Users.objects.get(user_username=request.session.get("user_username"))
        if user.role not in ["Admin", "Operations", "SalesAdmin", "SalesRep"]:
            return redirect("login")

        # Get specific order or return 404 if not found
        order = get_object_or_404(Orders, orderNum=order_id)

        # Fetch items for the specific order
        # This assumes that you have a related set of order items defined, replace 'order_items' with the correct related_name if needed
        order_items = order.order_items.all()

        # Render the view specific order template with order details and items
        return render(request, "viewSpecificOrder.html", {"order": order, "order_items": order_items, "user": user})

class OrderItemsForm(forms.ModelForm):
    class Meta:
        model = OrderItems
        fields = ('item', 'quantity')

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        if item and not quantity:
            self.add_error('quantity', "Quantity is required when item is selected.")

        if quantity and not item:
            self.add_error('item', "Item is required when quantity is specified.")

        return cleaned_data

class ProcessOrder(View):
    def get(self, request):
        # Fetch all orders
        orders = Orders.objects.filter(status="Placed")

        # Render the cancel order template
        return render(request, "processOrder.html", {"orders": orders})
     
    def post(self, request):
        order_id = request.POST.get('Order')
        order = Orders.objects.get(id=order_id)
        order_items = OrderItems.objects.filter(order=order)
        customer = order.Customer
        # Send Text Message
        sinch_client = Client(
        key_id="68db7cad-c377-4a64-a223-ad2a534ee18c",
        key_secret="PJBGjR6Gno-3rWl-t_OSIPFub~",
        project_id="26137e24-6715-4df3-936c-7005ff1c9945"
        )

        phone = "1"+ str(customer.phoneNumber)
        sinch_client.sms.batches.send(
        body="Hello from Sahil Inc.! Your Order has been processed. The Total ammount is " + str(order.orderAmount) + "." 
            "Thank you for shopping with us!",
        to=[phone],
        from_="12085810216",
        delivery_report="none"
        )


        # Prepare email content
        try: 
            subject = "Order Processed"
            name = order.Customer.cusFirstName + " " + order.Customer.CusLastName
            context = {
                'customer_name': name, 
                'order_items': order_items,
                'total_amount': order.orderAmount,
            }

            html_content = render_to_string('orderProcessed.html', context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[str(order.Customer.email)] 
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        except Exception as ex:
            print("Error sending email", ex)

        # Process the order
        order.status = "Processed"
        order.save()
        
        return redirect('/Operations')

class DeleteOrder(View):
    def get(self, request):
        # Fetch all orders
        orders = Orders.objects.all()

        # Render the cancel order template
        return render(request, "cancelOrder.html", {"orders": orders})
    
    def post(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        order_id = request.POST.get('Order')
        order = Orders.objects.get(id=order_id)
        print(order)
        order_items = OrderItems.objects.filter(order=order)
        print(order_items)

        # Send Text Message
        customer = order.Customer
        sinch_client = Client(
        key_id="68db7cad-c377-4a64-a223-ad2a534ee18c",
        key_secret="PJBGjR6Gno-3rWl-t_OSIPFub~",
        project_id="26137e24-6715-4df3-936c-7005ff1c9945"
        )

        phone = "1"+ str(customer.phoneNumber)
        sinch_client.sms.batches.send(
        body="Hello from Sahil Inc.! We would like to inform you that your order has been canceled." + 
            "While we regret doing business with you, we hope you will choose us again in the future.",
        to=[phone],
        from_="12085810216",
        delivery_report="none"
        )


        # Prepare email content
        try: 
            subject = "Order Cancellation"
            order_details = []
            for order_item in order_items:
                order_details.append({
                    'item_name': order_item.item.ItemName,
                    'item_quantity': order_item.quantity,
                    'item_price': order_item.item.ItemPrice
                })
            name = order.Customer.cusFirstName + " " + order.Customer.CusLastName
            context = {
                'customer_name': name,
                'order_details': order_details,
                'total_amount': order.orderAmount,
            }

            html_content = render_to_string('orderCancellation.html', context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[str(order.Customer.email)]  # Assuming the Customer model has an 'email' field
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        except Exception as ex:
            print("Error sending email", ex)

        # Delete the order after sending the email
        order_items.delete()
        order.delete()

        if user.role == "Admin":
            return redirect('/adminPage')
        elif user.role == "Operations":
            return redirect('/Operations')
        elif user.role == "SalesRep":
            return redirect("/SalesAdmin")

# ITEM ADD/DELTE

class AddItemView(View):
    def get(self, request):
        # Add authentication and permissions checks here if necessary
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            role = user.role
        except Exception as ex:
            return redirect("login")
        
        return render(request, "addItem.html", {"user": user})

    def post(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        item_name = request.POST.get('ItemName')
        item_number = request.POST.get('ItemNumber')
        item_price = request.POST.get('ItemPrice')

        # Check if the item number already exists
        if Items.objects.filter(ItemNumber=item_number).exists():
            messages.error(request, 'Item number already exists.')
            return render(request, "addItem.html", {"user": user})

        try:
            # Create and save the new item
            new_item = Items(ItemName=item_name, ItemNumber=item_number, ItemPrice=item_price)
            new_item.save()
            messages.success(request, 'Item added successfully.')

            # Redirect to the previous page
            if user.role == "Admin":
                return redirect('/adminPage')
            elif user.role == "Operations":
                return redirect('/Opeartions')

        except Exception as e:
            messages.error(request, f'Error adding item: {e}')
            return render(request, "addItem.html", {"user": user})

class DeleteItem(View):
    def get(self, request):
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
        except Exception as ex:
            return redirect("login")

        items = Items.objects.all()
        return render(request, 'deleteItem.html', {'items': items, "user": user})

    def post(self, request):

        user = Users.objects.get(user_username=request.session.get("user_username"))
        item_id = request.POST.get('Item')
        if not item_id:
            messages.error(request, 'No item selected.')
            return redirect('delete-item')  # Make sure to use the correct URL name

        try:
            item = Items.objects.get(id=item_id)
            item.delete()
            messages.success(request, 'Item deleted successfully.')
        except Items.DoesNotExist:
            messages.error(request, 'Item not found.')
        except Exception as e:
            messages.error(request, f'Error deleting item: {e}')

       # Redirect to the previous page
        if user.role == "Admin":
            return redirect('/adminPage')
            # elif user.role == "Operations":
            #     return redirect('/OpeartionsView')

# ADD SALESREP USER

class addSalesRep(View):
    def get(self, request):
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
        except Exception as ex:
            return redirect("login")
        
        if not Validations.checkLogin(self, request):
            return redirect("login")

        return render(request, "addSalesRep.html", {"user": user})

    def post(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        fullname = None
        username = None
        password = None
        region = None

        try:
            fullname = request.POST['fullname']
            username = request.POST['username']
            password = request.POST['password']
            region = request.POST['region']
            print(region)
            
            # validationx
            errors = validate.checkAddUserPost(fullname, username, password, "SalesRep", region)
            if len(errors) > 0:
                error_msg = 'Please correct the following: '
                for error in errors:
                    error_msg += error + '. '
                return render(request, "addSalesRep.html", {"message": error_msg})

        except Exception as ex:
            print("Exception: ", ex)
            return render(request, "addSalesRep.html", {"message": 'Something went wrong, check your information.'})
        try:

            if Users.objects.filter(user_username=username).exists():
                user_e = Users.objects.get(user_username=username)
                user_e.user_username = username
                user_e.user_password = password
                user_e.region = region

                # store personal information
                if user_e.info is None:
                    user_e.info = PersonalInfo.objects.create(myName=fullname)
                else:
                    user_e.info.myName = fullname
                    user_e.info.save()

                user_e.save()
            else:
                new_personal_info = PersonalInfo.objects.create(myName=fullname)
                newUser = Users.objects.create(user_username=username, user_password=password, role="SalesRep", region=region, info=new_personal_info)
                newUser.save()

            if user.role == "Admin":
                return redirect('/adminPage')
            elif user.role == "SalesAdmin":
                return redirect('/SalesAdmin')
            
        except Exception as ex:
            print("Exception: ", ex)
            return render(request, "addSalesRep.html", {"message": 'Something went wrong, check your information.'})
        
class deleteSalesReps(View):
    def get(self, request):
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
        except Exception as ex:
            return redirect("login")
        
        if not Validations.checkLogin(self, request):
            return redirect("login")
        salesreps = list(Users.objects.filter(role="SalesRep"))

        return render(request, "deleteSalesReps.html", {"user": user, "salesreps": salesreps})

    def post(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))

        try:
            Users.objects.get(id=request.POST['User']).delete()
        
            if user.role == "Admin":
                    return redirect('/adminPage')
            elif user.role == "SalesAdmin":
                    return redirect('/SalesAdmin')
        except Exception as ex:
            print("Exception:", ex)

        return render(request, "deleteSalesReps.html", {"user": user})
    
# ADMIN FUNCTIONALITY

class Admin(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        courses = list(Courses.objects.all())
        sections = list(Section.objects.all())
        users = list(Users.objects.exclude(role__in=["SalesRep", "cus"]))

        customers = list(Customer.objects.all())
        order = list(Orders.objects.all())
        sales = 0
        for o in order:
            sales += (o.orderAmount)

       
        
        items = list(Items.objects.all())
        salesreps = list(Users.objects.filter(role="SalesRep"))

        return render(request, "admin.html", {"courses": courses, "sections": sections, "users": users, "customers": customers, "orders": order, "sales": sales, "items": items, "salesreps": salesreps})

    def post(self, request):
        pass

# Sales Functionality

class SalesAdmin(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "SalesAdmin"):
            return redirect("login")
        
        orders = list(Orders.objects.all())
        # Get a list of salesreps
        salesreps = list(Users.objects.filter(role="SalesRep"))
        print(salesreps)
        sales = sum(o.orderAmount for o in orders)

        return render(request, "salesAdmin.html", {"orders": orders, "salesreps": salesreps, "sales": sales})

    def post(self, request):
        pass

class salesRep(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "SalesRep"):
            return redirect("login")

        # Get the region of the logged-in sales representative
        user = Users.objects.get(user_username=request.session.get("user_username"))
        region = user.region
        # Get customers in the sales rep's region
        customers = Customer.objects.filter(cusCity=region)
        order = Orders.objects.all()
        orders = []

        for i in order:
            if i.Customer in customers:
                orders.append(i)


        return render(request, "salesRep.html", {"customers": customers, "orders": orders})
    def post(self, request):
        pass

class Navigate(View):
    def get(self, request, customer_id):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        customer = Customer.objects.get(id=customer_id)

        customer_address = f"{customer.cusAddress}, {customer.cusCity}, {customer.cusState}, {customer.cusZip}"    
        user_address = f"{user.info.address}, {user.info.city}, {user.info.state}, {user.info.zip}"

        customer_location = self.geocode_address(customer_address)
        user_location = self.geocode_address(user_address)

        context = {
            'user_lat': user_location['lat'],
            'user_lng': user_location['lng'],
            'customer_lat': customer_location['lat'],
            'customer_lng': customer_location['lng'], 
            'cusAdd': customer_address, 
            'customer': customer
        }

        return render(request, "navigate.html", context)

    def geocode_address(self, address):
        api_file = open("Syllabus_Project/API_key.txt", "r")
        api_key = api_file.read()
        api_file.close()
        api_key = "AIzaSyD6v15JNhOvb1ex_lELHwV6RqF3DUBq-hQ"
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={api_key}"
        response = requests.get(url).json()
        if response['status'] == 'OK':
            return response['results'][0]['geometry']['location']
        else:
            return {'lat': 0, 'lng': 0}  # Default coordinates or error handling

# Operations Functionality

class Operations(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Operations"):
            return redirect("login")
        try:
            items = list(Items.objects.all())
            orders = list(Orders.objects.all())


            # Call render with the request object as the first parameter
            return render(request, "operations.html", {"items": items, "orders": orders})
        except Exception as ex:
            print("Exception:", ex)
            return redirect("login")
        
    def post(self, request):
        pass

# HR Functionality
class HR(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "HR"):
            return redirect("login")

        try:
            # Fetch all employees excluding Admin users
            employees = Users.objects.exclude(role="Admin")
        except Exception as ex:
            print("Exception:", ex)
            return redirect('login')
        
        return render(request, "hr.html", {"employees": employees})
    
    def post(self, request):
        pass

class ViewEmployeeInfo(View):
    def get(self, request):
        pass
    def post(self, request):
        pass

# Generate Pay checks
class GeneratePayCheck(View):
    def get(self, request):
        pass
    def post(self, request):
        pass

class CustomerView(View):
    def get(self, request):
        if not Validations.checkLogin(self, request):
            return redirect("login")
        user = Users.objects.get(user_username=request.session.get("user_username"))
        customer = Customer.objects.get(user=user)
        orders = list(Orders.objects.filter(Customer=customer))
        orderItemsDict = {}
        for order in orders:
            orderItems = OrderItems.objects.filter(order=order)
            orderItemsDict[order] = orderItems


        return render(request, "customer.html", {"customer": customer, "orders":orders, "orderItems":orderItemsDict})
    def post(self, request):
        pass
