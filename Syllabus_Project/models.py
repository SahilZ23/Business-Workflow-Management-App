from django.db import models
import uuid

# Create your models here.
class PersonalInfo(models.Model):
    myName = models.CharField(max_length=40)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=15, null=True, blank=True)
    state = models.CharField(max_length=10, null=True, blank=True)
    zip = models.IntegerField(max_length=6, null=True, blank=True)
    phoneNumber = models.CharField(max_length=40, null=False, blank=True)
    email = models.CharField(max_length=30, null=False, blank=True)

    def __str__(self):
        return f"{self.myName}"



ROLES = (
    ("Admin", "Admin"),
    ("SalesRep", "SalesRep"),
    ("SalesAdmin", "SalesAdmin"),
    ("HR", "HR"),
    ("Operations", "Operations"),
    ("cus", "cus"),
)

class Users(models.Model):
    role = models.CharField(max_length=20, choices=ROLES)
    user_username = models.CharField(max_length=20, unique=True)
    user_password = models.CharField(max_length=40)
    info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, blank=True, null=True)
    region = models.CharField(max_length=20, blank=True, null=True)  # Optional for some roles
    emp_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pay_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    hours = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.role != "SalesRep":
            self.region = None  # Clear region if role is not SalesRep
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_username}:{self.emp_id}"

    
### Create a model for the Inventory
class Items(models.Model):
    ItemName = models.CharField(max_length=40, null=False, blank=False)
    ItemNumber = models.IntegerField(unique=True)
    ItemPrice = models.DecimalField(unique=False)

    def __str__(self):
        return f"{self.ItemName}"

class Customer(models.Model):
    cusFirstName = models.CharField(max_length=40)
    CusLastName = models.CharField(max_length=40, default="")
    user = models.ForeignKey(Users, null=True, on_delete=models.CASCADE)
    # Can have an Office
    cusAddress = models.CharField(max_length=20, null=True, blank=True)
    cusCity = models.CharField(max_length=15, null=True, blank=True)
    cusState = models.CharField(max_length=10, null=True, blank=True)
    cusZip = models.IntegerField(max_length=6, null=True, blank=True)
    # Can have an Office Number if Office is marked
    phoneNumber = models.CharField(max_length=40, null=False, blank=True)
    email = models.EmailField(null=False, blank=False)

    def __str__(self):
        return f"{self.cusFirstName}"
    
### Create a model for the Inventory
class Items(models.Model):
    ItemName = models.CharField(max_length=40, null=False, blank=False)
    ItemPrice = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    ItemNumber = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.ItemName}"
    
### Create a modelfor the orders placed
class Orders(models.Model):
    orderNum = models.IntegerField(unique=True)
    Customer = models.ForeignKey(Customer, null =True, on_delete=models.SET_NULL)
    orderDate = models.DateField()
    orderAmount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, default="Placed", null=False, blank=False)

    def __str__(self):
        return f"{self.orderNum}"
    
### Create a model for items in an order
class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.order.orderNum} x {self.order.orderAmount}"

class Employee(models.Model):
    employee = models.ForeignKey(Users, on_delete=models.DO_NOTHING)
    emp_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pay_rate = models.DecimalField(max_digits=8, decimal_places=2)
    hours = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.user_username} - {self.employee_id}"

class Task(models.Model):
    rep = models.ForeignKey(Users, on_delete=models.DO_NOTHING, null=True, blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=50)
    description = models.TextField()
    complete_notes = models.TextField(default="", null=True, blank=True)

    def __str__(self):
        return self.description
    