"""
URL configuration for nyondo_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    # urls for supplier
    path('supplier/', views.supplier_list, name="supplier_list"),
    path('supplier/add/', views.add_supplier, name="add_supplier"),
    path('supplier/edit/<int:pk>/', views.edit_supplier, name="edit_supplier"),
    path('supplier/delete/<int:pk>/', views.delete_supplier, name="delete_supplier"),
    path('supplier_credit_list/',views.supplier_credit_list,name='supplier_credit_list'),
    path( 'supplier_credit_list/add_supplier_credit/',views.add_supplier_credit,name='add_supplier_credit'),
    path('pay_supplier_credit/<int:credit_id>/',views.pay_supplier_credit,name='pay_supplier_credit'),
    path('supplier_credit_detail/<int:credit_id>/',views.supplier_credit_detail,name='supplier_credit_detail'),
    # urls for stock
    path('stock_dashboard/', views.stock_dashboard, name="stock_dashboard"),
    path('stock/', views.stock_list, name="stock_list"),
    path('stock/add/', views.add_stock, name="add_stock"),
    path('stock/edit/<int:pk>/', views.edit_stock, name="edit_stock"),
    path('stock/details/<int:pk>/', views.stock_details, name="stock_details"),
    # urls for authetication
    path('login/', views.login, name="login"),

    # urls for sale
    path('sale/',views.sale_list, name="sale_list"),
    path('sale/add/', views.add_sale, name="add_sale"),
    path('sale/edit/<int:pk>/', views.edit_sale, name="edit_sale"),
    path('sale/details/<int:pk>/', views.sale_details, name= "sale_details"),
    path('sale_dashboard/', views.sale_dashboard, name="sale_dashboard"),
    path('sale/payment', views.payment, name="payment"),
    path('sale/sale_receipt/<int:pk>', views.sale_receipt, name="sale_receipt"),
    path('payment/add', views.add_payment, name="add_payment"),
    path('payment/history', views.payment_history, name="payment_history"),
    path('sale/customer_credit_list/', views.credit_list, name="credit_list"),
    path('deposit_list/', views.deposit_list, name="deposit_list"),
    path('deposit_list/deposit_receipt/<int:pk>/', views.deposit_receipt, name="deposit_receipt"),
    path('deposit_list/add/', views.add_deposit, name="add_deposit"),
    path('deposit_list/edit/<int:pk>/', views.edit_deposit, name="edit_deposit"),
    # urls for customer
    path('customer/', views.customer_list, name="customer_list"),
    path('customer/add/', views.add_customer, name="add_customer"),
    path('customer/edit/<int:pk>/', views.edit_customer, name="edit_customer"),
    path('customer/delete/<int:pk>/', views.delete_customer, name="delete_customer"),
    
    # url for the admin dashboard
    path('admin_dashboard/', views.admin_dashboard, name="admin_dashboard"),

    # url for  the report
    path('reports/', views.reports_dashboard , name="reports_dashboard"),
]
