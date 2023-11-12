from Syllabus_Project.models import Users, Courses, PersonalInfo, Section, Policies, ROLES
import re

class Validations():
    def checkDuplicateCourse(self, courseName, courseNum, courseYear, courseSem):
        courses = Courses.objects.filter(courseName=courseName, courseNumber=courseNum, year=courseYear, semester=courseSem)
        return len(courses) != 0

    def checkCoursePost(self, courseName, courseNum, courseYear, courseSem):
        #global course_name, course_sem, course_num, course_year
        has_alpha_regex = re.compile('[A-Za-z\s]+[\d]*')
        is_numeric_regex = re.compile('^[\d]+$')
        errors = []
        parse_will_fail = False

        if not has_alpha_regex.match(courseName):
            errors.append("Course name should start as alphabetic")

        if not has_alpha_regex.match(courseSem):
            errors.append("Course semester should start as alphabetic")

        if not is_numeric_regex.match(courseNum):
            errors.append("Course number must be a positive integer")
            parse_will_fail = True

        if not is_numeric_regex.match(courseYear):
            errors.append("Course year must be a positive integer")
            parse_will_fail = True

        if not parse_will_fail:
            try:
                course_num = int(courseNum)
                course_year = int(courseYear)

                if course_num <= 0:
                    errors.append("Course number must be a positive integer")

                if course_year <= 0:
                    errors.append("Course year must be a positive integer")

            except(ValueError, TypeError):
                errors.append("Could not parse numeric input")

        return errors
        #self.checkDuplicateCourse(courseName, courseNum, courseYear, courseSem)

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

        if is_numeric_regex.match(region):
            errors.append("Region cannot have numbers")
            
        # this can be used for password requirements in the future
        if len(password) == 0:
            errors.append("Password is required")
        elif len(password) == 1:
            errors.append("Password is weak")
        return errors

    # return whether a user is permitted to update the policy for a course
    def userCanAddPolicy(self, user, course):
        if user.role != "Instructor":
            return False

        if len(Section.objects.filter(courses=course, users=user)) > 0:
            return True
        else:
            return False

    def checkSectionPost(self, course, user):
        if user.role == "Instructor" and Section.objects.filter(courses__id=course.id, users__role="Instructor").exists():
            return "Professor already assigned to this course"
        return ""


        # Example: errors = validate.checkCustomerInfoPost(cusName, cusAddress, phoneNumber, email)
        # Check for validation errors
        # Example: if len(errors) > 0:
        #     error_msg = 'Please correct the following: '
        #     for error in errors:
        #         error_msg += error + '. '
        #     return render(request, "customer_form.html", {"message": error_msg})