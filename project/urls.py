"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from Syllabus_Project.views import Login, Admin,  AddUser, DeleteUsers,  AddCustomer, SalesAdmin, DeleteCustomer, \
     AddOrder, DeleteOrder, ViewOrders, AddItemView, DeleteItem, addSalesRep, deleteSalesReps, Operations,salesRep, HR, \
     ViewEmployeeInfo, AddPersonalInfo, Navigate,ProcessOrder, verify, CustomerView, PasswordReset, GeneratePayCheck, \
     RequestOrderCancellation, AddTaskView, CompleteTaskView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Login.as_view(), name="login"),
    path('Verify', verify.as_view(), name="Verify"),
    path('adminPage', Admin.as_view(), name="adminPage"),
    path('addUser', AddUser.as_view(), name="adduser"),
    path('deleteUser', DeleteUsers.as_view(), name='deleteUser'),
    path('addCustomer', AddCustomer.as_view(), name="addCustomer"),
    path('SalesAdmin', SalesAdmin.as_view(), name="SalesAdmin"),
    path('deleteCustomer', DeleteCustomer.as_view(), name="deleteCustomer"),
    path('addOrder', AddOrder.as_view(), name="addOrder"),
    path('deleteOrder', DeleteOrder.as_view(), name="deleteOrder"),
    path('viewOrder', ViewOrders.as_view(), name="viewOrder"),
    path('addItem', AddItemView.as_view(), name="addItem"),
    path('deleteItem', DeleteItem.as_view(), name="deleteItem"),
    path('addSalesRep', addSalesRep.as_view(), name ="addSalesRep"),
    path('deleteSalesRep', deleteSalesReps.as_view(), name ="deleteSalesRep"),
    path('viewOrder/<int:order_id>/', ViewOrders.as_view(), name="viewSpecificOrder"),
    path('Operations', Operations.as_view(), name="Operations"),
    path('salesRep', salesRep.as_view(), name="salesRep"),
    path('HR', HR.as_view(), name="HR"),
    path('customer', CustomerView.as_view(), name="customer"),
    path('viewEmployee', ViewEmployeeInfo.as_view(), name="viewEmployee"),
    path('AddPersonalInfo/<uuid:user_id>/', AddPersonalInfo.as_view(), name='AddPersonalInfo'),
    path('AddPersonalInfo', AddPersonalInfo.as_view(), name="AddPersonalInfo"),
    path('Navigate/<int:customer_id>/', Navigate.as_view(), name="Navigate"),
    path('ProcessOrder/', ProcessOrder.as_view(), name="ProcessOrder"),
    path('PasswordReset', PasswordReset.as_view(), name="PasswordReset"),
    path('GeneratePay', GeneratePayCheck.as_view(), name="GeneratePay"),
    path('requestCancellation', RequestOrderCancellation.as_view(), name="requestCancellation"),
    path('addtask/', AddTaskView.as_view(), name='add_task'),
    path('complete-task/', CompleteTaskView.as_view(), name='complete-task'),
   ]
