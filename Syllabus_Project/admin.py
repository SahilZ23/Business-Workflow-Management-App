from django.contrib import admin
from .models import PersonalInfo, Courses, Users, Section, Policies, Customer, Items, Orders
# Register your models here.
admin.site.register(PersonalInfo)
admin.site.register(Courses)
admin.site.register(Users)
admin.site.register(Section)
admin.site.register(Policies)

# Register the models for CS995
admin.site.register(Customer)
admin.site.register(Items)
admin.site.register(Orders)

