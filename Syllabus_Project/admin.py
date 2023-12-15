from django.contrib import admin
from .models import PersonalInfo, Courses, Users, Section, Policies, Customer, Items, Orders, OrderItems, Employee, Task
# Register your models here.

admin.site.register(Users)
admin.site.register(PersonalInfo)
admin.site.register(Customer)
admin.site.register(Items)
admin.site.register(Orders)
admin.site.register(OrderItems)
admin.site.register(Employee)
admin.site.register(Task)

