import re
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from Syllabus_Project.models import Users, Courses, PersonalInfo, Section, Policies, Customer, Orders, Items
from Syllabus_Project.Validations import Validations

validate = Validations()


# Create your views here.
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
        print(users)
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

                ##################  TO ADD  ##############################
                # if u.role == "SalesRep":
                #     request.session["user_username"] = username
                #     return redirect("SalesRepView")
                # if u.role == "HR":
                #     request.session["user_username"] = username
                #     return redirect("HRView")
                # if u.role == "Operations":
                #     request.session["user_username"] = username
                #     return redirect("OperartionsView")
 
            else:
                message = "Invalid Username/Password"
        else:
            message = "Invalid Username/Password"
        return render(request, "login.html", {"message": message})


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


class AddUser(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        return render(request, "adduser.html")

    def post(self, request):
        fullname = None
        username = None
        password = None
        role = None

        try:
            fullname = request.POST['fullname']
            username = request.POST['username']
            password = request.POST['password']
            role = request.POST['role']

            # validation
            errors = validate.checkAddUserPost(fullname, username, password, role)
            if len(errors) > 0:
                error_msg = 'Please correct the following: '
                for error in errors:
                    error_msg += error + '. '
                return render(request, "adduser.html", {"message": error_msg})

        except Exception as ex:
            return render(request, "adduser.html", {"message": 'Something went wrong, check your information.'})

        if Users.objects.filter(user_username=username).exists():
            user = Users.objects.get(user_username=username)
            user.user_username = username
            user.user_password = password
            user.role = role

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
                                           info=new_personal_info)
            newUser.save()

        return Admin.get(self, request)


class Admin(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Admin"):
            return redirect("login")

        courses = list(Courses.objects.all())
        sections = list(Section.objects.all())
        users = list(Users.objects.exclude(role="SalesRep"))

        customers = list(Customer.objects.all())
        order = list(Orders.objects.all())
        print(order)
        sales = 0
        for o in order:
            sales += int(o.orderAmount)

        print(sales)
        
        items = list(Items.objects.all())
        salesreps = list(Users.objects.filter(role="SalesRep"))


        return render(request, "admin.html", {"courses": courses, "sections": sections, "users": users, "customers": customers, "orders": order, "sales": sales, "items": items, "salesreps": salesreps})

    def post(self, request):
        pass


class AddPersonalInfo(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Instructor", "TA"):
            return redirect("login")

        # make sure the request is for a valid user that exists
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            role = user.role
        except Exception as ex:
            return redirect("login")

        return render(request, "personalInfo.html", {"user": user, "role": role})

    def post(self, request):
        daysString = ""
        user = None
        pi = None
        name = None
        loc = None
        num = None
        p_num = None
        email = None
        startTime = None
        endTime = None
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            pi = Users.objects.get(user_username=request.session.get("user_username"))
            name = request.POST.get('name')
            loc = request.POST.get('OfficeLocation')
            num = request.POST.get('OfficeNumber')
            p_num = request.POST.get('PhoneNumber')
            email = request.POST.get('email')
            startTime = request.POST['startTime']
            endTime = request.POST['endTime']

            # validation
            errors = validate.checkPersonalInfoPost(name=name, officeLocation=loc, officeNumber=num, phoneNumber=p_num, email=email)
            if len(errors) > 0:
                error_msg = 'Please correct the following: '
                for error in errors:
                    error_msg += error + '. '
                return render(request, "personalInfo.html", {"message": error_msg})

        except Exception as ex:
            return render(request, "personalInfo.html", {"message": 'Something went wrong, check your information.'})

        # read the days checkboxes
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        for day in days:
            if day in request.POST.keys():
                if len(daysString) != 0:
                    daysString += ', '
                daysString += day

        if PersonalInfo.objects.filter(myName=name).exists():
            PersonalInfo.objects.filter(myName=name).update(officeLocation=loc,
                                                            officeNumber=num,
                                                            phoneNumber=p_num,
                                                            email=email,
                                                            day=daysString,
                                                            timeFrom=startTime,
                                                            timeTo=endTime)
        else:
            pi = PersonalInfo(myName=name,
                              officeLocation=loc,
                              officeNumber=num,
                              phoneNumber=p_num,
                              email=email,
                              day=daysString,
                              timeFrom=startTime,
                              timeTo=endTime)
            pi.save()
            user.info = pi
            user.save()
            print(pi)

        if user.role == "Instructor":
            return redirect('/userView')
        else:
            return redirect('/TAView')


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

class SalesAdmin(View):
    def get(self, request):
        if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "SalesAdmin"):
            return redirect("login")

        role = ""
        orders = list(Orders.objects.all())
        # Get a list of salesreps
        salesreps = list(Users.objects.filter(role="SalesRep"))
        print(salesreps)
        sales = 0
        for o in orders:
            sales += int(o.orderAmount)

        return render(request, "salesAdmin.html", {"courses": orders, "salesreps": salesreps, "sales": sales})

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


class DeleteUsers(View):
    def get(self, request):
        users = list(Users.objects.all())
        return render(request, "deleteUsers.html", {"users": users})

    def post(self, request):
        Users.objects.get(id=request.POST['User']).delete()
        return redirect('/adminPage')


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

#CUSTOMER ADD/EDIT + DELETE

class AddCustomer(View):
    def get(self, request):
        # Add your authentication and role checks here if necessary
        # if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Instructor", "TA"):
        #     return redirect("login")

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
            customer = Customer(cusName=cusName, cusAddress=cusAddress, phoneNumber=phoneNumber, email=email)
            customer.save()
            
            if user.role == "Admin":
                return redirect('/adminPage')
            elif user.role == "SalesAdmin":
                return redirect('/SalesAdminView')

        except Exception as ex:
            return render(request, "addCustomer.html", {"message": 'Something went wrong, check your information.'})
        
class DeleteCustomer(View):
    def get(self, request):
        customers = list(Customer.objects.all())
        return render(request, "deleteCustomer.html", {"customers": customers})

    def post(self, request):
        Customer.objects.get(id=request.POST['Customer']).delete()
        return redirect('/adminPage')
    

# ORDER ADD/EDIT + DELETE

class AddOrder(View):
    def get(self, request):
        # Add your authentication and role checks here if necessary
        # if not Validations.checkLogin(self, request) or not Validations.checkRole(self, request, "Instructor", "TA"):
        #     return redirect("login")

        # Make sure the login request is from a valid user.
        try:
            user = Users.objects.get(user_username=request.session.get("user_username"))
            role = user.role
            customers = Customer.objects.all()
        except Exception as ex:
            return redirect("login")

        # render the create customer form
        return render(request, "addOrder.html", {"user": user, "role": role, "customers": customers})  

    def post(self, request):
        # Retrieve and validate customer data from the POST request
        user = Users.objects.get(user_username=request.session.get("user_username"))
        orderNum = request.POST.get('orderNum')
        print(orderNum)
        customer = Customer.objects.get(id=request.POST['Customer'])
        print(customer)
        orderDate = request.POST.get('orderDate')
        print(orderDate)
        orderAmount = request.POST.get('orderAmount')
        print(orderAmount)

        # Perform validation using your validation module (if needed)

        try:
            # Create a new order instance and save it to the database
            order = Orders(orderNum=orderNum, Customer=customer, orderDate=orderDate, orderAmount=orderAmount)
            order.save()
            
            if user.role == "Admin":
                return redirect('/adminPage')
            # elif user.role == "Operations":
            #     return redirect('/OpeartionsView')

        except Exception as ex:
            print("Exception occured: ", ex)
            return render(request, "addOrder.html", {"message": 'Something went wrong, check your information.'})

class ViewOrders(View):
    def get(self, request):
        # Authentication and role checks
        user = Users.objects.get(user_username=request.session.get("user_username"))
        if user.role not in ["Admin", "Operations"]:
            return redirect("login")

        # Fetch all orders
        orders = Orders.objects.all()

        # Render the view orders template
        return render(request, "viewOrders.html", {"orders": orders, "user": user})

class DeleteOrder(View):
    def get(self, request):
        # Fetch all orders
        orders = Orders.objects.all()

        # Render the cancel order template
        return render(request, "cancelOrder.html", {"orders": orders})

    def post(self, request):
        # Retrieve and delete the specified order
        order_id = request.POST.get('Order')
        Orders.objects.filter(id=order_id).delete()

        # Redirect after deletion
        return redirect('/adminPage')  # Adjust the redirection as needed
    



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
            return render(request, "addItem.html")

        try:
            # Create and save the new item
            new_item = Items(ItemName=item_name, ItemNumber=item_number, ItemPrice=item_price)
            new_item.save()
            messages.success(request, 'Item added successfully.')

            # Redirect to the previous page
            if user.role == "Admin":
                return redirect('/adminPage')
            # elif user.role == "Operations":
            #     return redirect('/OpeartionsView')

        except Exception as e:
            messages.error(request, f'Error adding item: {e}')
            return render(request, "addItem.html")

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

class OperationsView(View):
    def get(self, request):
        pass
    def post(self, request):
        pass

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