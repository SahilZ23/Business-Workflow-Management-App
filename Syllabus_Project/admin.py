from django.contrib import admin
from .models import PersonalInfo, Courses, Users, Section, Policies, CustomerInfo, ItemInfo, SalesData
# Register your models here.
admin.site.register(PersonalInfo)
admin.site.register(Courses)
admin.site.register(Users)
admin.site.register(Section)
admin.site.register(Policies)
admin.site.register(CustomerInfo)
admin.site.register(ItemInfo)
admin.site.register(SalesData)

