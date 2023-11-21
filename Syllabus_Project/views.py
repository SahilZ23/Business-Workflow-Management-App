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

validate = Validations()


# Create your views here.

class AddCourse(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        users = Users.objects.all()
        return render(request, "addCourse.html", {"users": users})

    def post(self, request):
        course_name = request.POST.get('course')
        course_num = request.POST.get('courseNumber')
        sem = request.POST.get('semester')
        year = request.POST.get('year')

        errors = validate.checkCoursePost(course_name, course_num, year, sem)
        if len(errors) != 0:
            return render(request, "addCourse.html", {"users": Users.objects.all(), "errors": errors})
        else:
            if Courses.objects.filter(courseNumber=course_num).exists():
                Courses.objects.filter(courseNumber=course_num).update(courseName=course_name,
                                                                       semester=sem,
                                                                       year=year
                                                                       )
                message = "Successfully edited a course"

            else:
                course = Courses(courseName=course_name, courseNumber=course_num, semester=sem, year=year)
                course.save()

                message = "Successfully created a course"

            return render(request, "admin.html",
                          {"message": message, "courses": Courses.objects.all(), "users": Users.objects.all(),
                           "sections": Section.objects.all()})

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
            # errors = validate.checkPersonalInfoPost(name=name, address=address, phoneNumber=p_num, email=email)
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


class userView(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Instructor"):
            return redirect("login")

        courses = list(Section.objects.filter(users__user_username=request.session.get("user_username")))
        return render(request, "userView.html", {"courses": courses})

    def post(self, request):
        pass

class TAView(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "TA"):
            return redirect("login")

        courses = list(Section.objects.filter(users__user_username=request.session.get("user_username")))
        return render(request, "TApage.html", {"courses": courses})

    def post(self, request):
        pass

class Policy(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Instructor"):
            return redirect("login")

        courses = list(Section.objects.filter(users__user_username=request.session.get("user_username")))

        return render(request, "addPolicy.html", {'courses': courses})

    def post(self, request):
        try:
            policy_name = request.POST.get('policyName')
            policies = request.POST.get('policyText')
            course_id = request.POST.get('course')

            user = Users.objects.get(user_username=request.session.get('user_username'))
            course = Courses.objects.get(id=course_id)

            if not validate.userCanAddPolicy(user, course):
                return render(request, "addPolicy.html", {
                    'courses': list(Section.objects.filter(users__user_username=request.session.get("user_username"))),
                    'error': "User is not the instructor for the selected course. Policy change denied."})

            # add or edit policy
            if len(Policies.objects.filter(policy_course=course, policy_user=user)) > 0:
                policy_obj = Policies.objects.get(policy_course=course, policy_user=user)
                policy_obj.policies = policies
                policy_obj.policy_name = policy_name
                policy_obj.save()
            else:
                Policies.objects.create(policy_name=policy_name, policies=policies, policy_user=user,
                                        policy_course=course)

            courses = list(Section.objects.filter(users__user_username=request.session.get("user_username")))
            return render(request, "userView.html", {"courses": courses})

        except Policies.MultipleObjectsReturned:
            return render(request, "addPolicy.html", {
                'courses': list(Section.objects.filter(users__user_username=request.session.get("user_username"))),
                'error': "Error: the database has multiple policies for this course and user, please connect to the database and delete the duplicates."})
        
        except Exception as ex:
            return render(request, "addPolicy.html", {
                'courses': list(Section.objects.filter(users__user_username=request.session.get("user_username"))),
                'error': "An error occurred, please check your inputs."})

class AddSection(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        courses = list(Courses.objects.all())
        users = list(Users.objects.all())

        return render(request, "addSection.html", {'courses': courses, 'users': users})

    def post(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        # get variables
        try:
            sectionNumber = request.POST["sectionNumber"]
            startTime = request.POST['startTime']
            endTime = request.POST['endTime']
            daysString = ""
            room = request.POST['sectionRoom']
            course = Courses.objects.get(id=request.POST['Course'])
            user = Users.objects.get(id=request.POST['User'])

            # read the days checkboxes
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

            for day in days:
                if day in request.POST.keys():
                    if len(daysString) != 0:
                        daysString += ', '
                    daysString += day

            error = Validations.checkSectionPost(self, course, user)
            print(error)
            if len(error) > 0:
                return render(request, "addSection.html", {'courses': list(Courses.objects.all()), 'users': list(Users.objects.all()), 'error': error})

            if Section.objects.filter(section_number=sectionNumber).exists():

                sect = Section.objects.filter(section_number=sectionNumber).update(timeFrom=startTime,
                                                                                   timeTo=endTime,
                                                                                   class_room=room,
                                                                                   day=daysString,
                                                                                   courses=course,
                                                                                   users=user)
                print("Section exists", sect)

            else:
                sect = Section(section_number=sectionNumber,
                               timeFrom=startTime,
                               timeTo=endTime,
                               class_room=room,
                               day=daysString,
                               courses=course,
                               users=user)

                sect.save()

        except Exception as ex:
            courses = list(Courses.objects.all())
            users = list(Users.objects.all())
            return render(request, "addSection.html",
                          {'courses': courses, 'users': users, 'error': 'Form response missing inputs: ' + str(ex)})

        return Admin.get(self, request)

class DeleteCourses(View):
    def get(self, request):
        courses = list(Courses.objects.all())
        return render(request, "deleteCourses.html", {"courses": courses})

    def post(self, request):
        Courses.objects.get(id=request.POST['Course']).delete()
        return redirect('/adminPage')

class DeleteSections(View):
    def get(self, request):
        sections = list(Section.objects.all())
        return render(request, "deleteSection.html", {"sections": sections})

    def post(self, request):
        Section.objects.get(id=request.POST['Section']).delete()
        return redirect('/adminPage')

class Syllabus(View):
    def get(self, request, year, semester, courseNumber):
        try:
            section = Section.objects.get(courses__courseNumber=courseNumber,
                                          courses__semester=semester, courses__year=year, users__role="Instructor")
            course = section.courses
            labs = Section.objects.filter(courses=course, users__role="TA")
            info = section.users.info
            policies = Policies.objects.filter(policy_course__courseNumber=courseNumber)

            return render(request, "syllabus.html", {"section": section, "course": course,
                                                     "info": info, "policies": policies, "labs": labs})

        except Section.DoesNotExist:
            return render(request, "syllabus.html", {
                'error': "Not found. Either the year, semester or course you are looking for does not exist, "
                         "or the syllabus has not been created yet."})

    def post(self, request):
        pass

class Login(View):
    def get(self, request):
        # request.session.pop("user_username", None)
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("loginEmail")
        password = request.POST.get("loginPassword")
        print(username, password)
        message = ""
        users = list(Users.objects.filter(user_username=username))
        if len(users) != 0:
            u = users[0]
            if u.user_password == password:
                if u.role == "Admin":
                    request.session["user_username"] = username
                    return redirect("adminPage")
                if u.role == "TA":
                    request.session["user_username"] = username
                    return redirect("TAView")
                if u.role == "Instructor":
                    request.session["user_username"] = username
                    return redirect("userView")
                if u.role == "SalesAdmin":
                    request.session["user_username"] = username
                    return redirect("SalesAdmin")            
                if u.role == "Operations":
                    request.session["user_username"] = username
                    return redirect("Operations")
                if u.role == "SalesRep":
                    request.session["user_username"] = username
                    return redirect("salesRep")
                if u.role == "HR":
                    request.session["user_username"] = username
                    return redirect("HR")
                
 
            else:
                message = "Invalid Username/Password"
        else:
            message = "Invalid Username/Password"
        return render(request, "login.html", {"message": message})

class Admin(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        courses = list(Courses.objects.all())
        sections = list(Section.objects.all())
        users = list(Users.objects.exclude(role="SalesRep"))

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
                user.info = PersonalInfo.objects.create(myName=fullname)
            else:
                user.info.myName = fullname
                user.info.save()

            user.save()
        else:
            new_personal_info = PersonalInfo.objects.create(myName=fullname)
            newUser = Users.objects.create(user_username=username, user_password=password, role=role,
                                           info=new_personal_info, region=region)
            newUser.save()

        return Admin.get(self, request)

class DeleteUsers(View):
    def get(self, request):
        users = list(Users.objects.exclude(role="SalesRep"))
        return render(request, "deleteUsers.html", {"users": users})

    def post(self, request):
        Users.objects.get(id=request.POST['User']).delete()
        return redirect('/adminPage')

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
        cusName = request.POST.get('cusName')
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
            # Create a new Customer instance and save it to the database
            customer = Customer(cusName=cusName, cusAddress=cusAddress, cusCity=cusCity, cusState=cusState, cusZip=cusZip, phoneNumber=phoneNumber, email=email)
            customer.save()
            
            print(customer.id)
            if user.role == "Admin":
                return redirect('/adminPage')
            if user.role == "SalesAdmin":
                return redirect('/SalesAdminView')
            elif user.role == "SalesRep":
                return redirect("salesRep")
            

        except Exception as ex:
            return render(request, "addCustomer.html", {"message": 'Something went wrong, check your information.'})
        
class DeleteCustomer(View):
    def get(self, request):
        customers = list(Customer.objects.all())
        return render(request, "deleteCustomer.html", {"customers": customers})

    def post(self, request):
        Customer.objects.get(id=request.POST['Customer']).delete()
        return redirect('/adminPage')
    

# ORDER ADD/EDIT + DELETE + VIEW

class AddOrder(View):
    def get(self, request):
        # if not Validations.checkLogin(request) or Validations.checkRole(request, ["SalesRep", "HR", "SalesAdmin"]):
        #     return redirect("login")
        
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            customers = Customer.objects.all()
            OrderItemFormset = modelformset_factory(OrderItems, fields=('item', 'quantity'), extra=1)
            formset = OrderItemFormset(queryset=OrderItems.objects.none())
        except Exception as ex:
            return redirect("login")
        
        return render(request, "addOrder.html", {"user": user, "customers": customers, "formset": formset})
    def post(self, request):
        user = Users.objects.get(user_username=request.session.get("user_username"))
        OrderItemFormset = modelformset_factory(OrderItems, fields=('item', 'quantity'), extra=1)
        formset = OrderItemFormset(request.POST)

        order_amount = 0

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

                if formset.is_valid():
                    # Temporarily save the order to associate it with order items
                    order.save()

                    # Create order items and calculate the total amount
                    for form in formset:
                        order_item = form.save(commit=False)
                        order_item.order = order
                        item_price = order_item.item.ItemPrice  # Assuming ItemPrice is a field on the related Items model
                        order_amount += item_price * order_item.quantity
                        order_item.save()

                    # Update the order amount and save the order again
                    order.orderAmount = order_amount
                    order.save()

                # # Send an email to the customer when order is placed.
                # try: 
                #     subject = "Order Confirmation"
                #     context = {
                #             'customer_name': customer.cusName, 
                #             'order_items': order_item.item.ItemName,  
                #             'total_amount': order_amount,
                #         }
                #     html_content = render_to_string('orderConfirmation.html', context)
                #     text_content = strip_tags(html_content)  # Fallback for plain text email clients
                    
                #     message = html_content
                #     print(message)
                #     email = str(customer.email)
                #     print(email)
                #     send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=True)

                # except Exception as ex:
                #     print("Email sending failed: ", ex)
                try: 
                    subject = "Order Confirmation"
                    context = {
                        'customer_name': customer.cusName, 
                        'item_name': order_item.item.ItemName,  
                        'item_quantity': order_item.quantity,
                        'item_price': order_item.item.ItemPrice,
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
                    return redirect("/SalesAdmin")

            except Exception as ex:
                print("Exception:", ex)
                return render(request, "addOrder.html")
        
class ViewOrders(View):
    def get(self, request, order_id=None):
        # Check if an order_id is provided
        if order_id:
            return self.view_specific_order(request, order_id)
        
        # Authentication and role checks
        user = Users.objects.get(user_username=request.session.get("user_username"))
        if user.role not in ["Admin", "Operations", "SalesAdmin"]:
            return redirect("login")

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

class DeleteOrder(View):
    def get(self, request):
        # Fetch all orders
        orders = Orders.objects.all()

        # Render the cancel order template
        return render(request, "cancelOrder.html", {"orders": orders})
    
    def post(self, request):
        order_id = request.POST.get('Order')
        order = Orders.objects.get(id=order_id)
        print(order)
        order_items = OrderItems.objects.get(order=order)
        print(order_items)
        # Prepare email content
        try: 
            subject = "Order Cancellation"
            context = {
                'customer_name': order.Customer.cusName, 
                'item_name': order_items.item.ItemName,  
                'item_quantity': order_items.quantity,
                'item_price': order_items.item.ItemPrice,
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
        order.delete()

        return redirect('/adminPage')

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
                newUser = Users.objects.create(user_username=username, user_password=password, role="SalesRep", info=new_personal_info)
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
            'customer_lng': customer_location['lng']
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