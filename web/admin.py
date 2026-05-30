from django.contrib import admin
from . models import SupplierCredit
from . models import Supplier
from . models import Sale
from . models import Stock
from . models import Customer
from . models import Deposit
from . models import Payment

# Register your models here.

admin.site.register(Supplier)
admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(Customer)
admin.site.register(SupplierCredit)
admin.site.register(Deposit)
admin.site.register(Payment)


