from django.db import models


# Create your models here.
class PersonalInfo(models.Model):
    myName = models.CharField(max_length=40)
    # Can have an Office
    officeLocation = models.CharField(max_length=20, null=True, blank=True)
    # Can have an Office Number if Office is marked
    officeNumber = models.IntegerField(null=True, blank=True)
    phoneNumber = models.CharField(max_length=40, null=False, blank=True)
    email = models.CharField(max_length=30, null=False, blank=True)
    # Can have the days they are in office if they have declared an Office number
    day = models.CharField(max_length=50, null=True)
    # The time they work during the bussiness days
    timeFrom = models.TimeField("Date Published", null=True)
    timeTo = models.TimeField("DatePublished", null=True)

    def __str__(self):
        return f"{self.myName}"


class Courses(models.Model):
    courseName = models.CharField(max_length=100)
    courseNumber = models.IntegerField()  # courseNumber should be unique and no course will have the same courseNumber
    semester = models.CharField(max_length=40)  # Fall, Spring, Winter, and Summer semesters
    year = models.IntegerField()

    #section = models.IntegerField(unique=True)  # sections should also be unique for lecture, lab, discussion
    # https://stackoverflow.com/questions/2201598/how-to-define-two-fields-unique-as-couple

    def __str__(self):
        return f"{self.courseName} - {self.courseNumber}"


ROLES = (
    ("TA", "TA"),
    ("Instructor", "Instructor"),
    ("Admin", "Admin"),
)


class Users(models.Model):
    role = models.CharField(max_length=20, choices=ROLES)

    user_username = models.CharField(max_length=20)
    user_password = models.CharField(max_length=40)

    # Personal info will have many users' personal info but every user has only one personal information
    info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, blank=True, null=True)

    # ManyToManyField is basically a foreign key in which it creates a bridge
    # by connecting courses having many users and users having many courses
    #courses = models.ManyToManyField(Courses, blank=True)

    def __str__(self):
        return f"{self.role}:{self.user_username}"


class Policies(models.Model):
    policies = models.TextField()

    # An instructor can write multiple policies in different courses but each policy is created by one instructor
    policy_user = models.ForeignKey(Users, on_delete=models.CASCADE)

    # courses ??
    policy_course = models.ForeignKey(Courses, on_delete=models.CASCADE)

    policy_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.policy_name}"

class Section(models.Model):
    day = models.CharField(max_length=50)
    timeFrom = models.TimeField("Date Published")
    timeTo = models.TimeField("DatePublished")
    class_room = models.CharField(max_length=40)
    section_number = models.IntegerField()

    #An User (Instructor or TA) might be in different sections, but each section contains only one User (Instructor or TA)
    users = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)

    #A course can have multiple sections but each section contains one course
    courses = models.ForeignKey(Courses, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('section_number','courses')

    def __str__(self):
        return f"{self.courses.courseNumber} - {self.section_number}"
    
### Create a model for the Inventory
class Items(models.Model):
    ItemName = models.CharField(max_length=40, null=False, blank=False)
    ItemNumber = models.IntegerField(unique=True)

### Create a model for the Inventory
class Items(models.Model):
    ItemName = models.CharField(max_length=40, null=False, blank=False)
    ItemNumber = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.ItemName}"

### A model that can have the ammount of sales dome in total
class Sales(models.Model):
    salesAmmmount = models.ForeignKey(Orders, on_delete=models.CASCADE)


