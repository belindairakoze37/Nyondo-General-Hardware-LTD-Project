from django.contrib import admin
from . models import *

# Register your models here.

admin.site.register(Supplier)
admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(Customer)
admin.site.register(SupplierCredit)
admin.site.register(Deposit)
admin.site.register(Payment)


