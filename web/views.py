import re
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render,redirect,get_object_or_404
from web.models import Supplier
from web.models import Stock
from web.models import Sale
from web.models import Customer
from web.models import Payment
from web.models import Deposit
from web.models import SupplierCredit
from decimal import Decimal
import datetime
from datetime import timedelta
from django.db.models import Sum, Count 
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
   
    return render(request,"index.html")



    
@login_required
def stock_list(request):
    all_stocks = Stock.objects.all()
    

    # Get search text
    search_query = request.GET.get("q")

    # Search product name
    if search_query:
        all_stocks = all_stocks.filter(
            product_name__icontains=search_query
        )

    context = {
        "stocks": all_stocks
    }

    return render(request, "stock_list.html", context)

@login_required
def add_stock(request):
 # Needed for dropdown 
    suppliers = Supplier.objects.all() 

    if request.method == "POST":
        payload = request.POST

        supplier_id = payload.get("supplier")
        supplier = Supplier.objects.get(id=supplier_id)  

        newStock = Stock()
        newStock.product_name = payload.get("product_name")
        newStock.quantity = int(payload.get("quantity"))
        newStock.unit_cost = Decimal(payload.get("unit_cost"))   
        newStock.selling_price = Decimal(payload.get("selling_price"))  
        newStock.category = payload.get("category")
        newStock.supplier = supplier 
        newStock.unit = payload.get("unit")  
        newStock.payment_method = payload.get("payment_method") 
        newStock.is_paid = payload.get("is_paid") == "on"
        newStock.credit_due_date = payload.get("credit_due_date") or None


        newStock.save()
        return redirect('stock_list')

    return render(request, "add_stock.html", {"suppliers": suppliers})

@login_required
def edit_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    suppliers = Supplier.objects.all()  

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        supplier = Supplier.objects.get(id=supplier_id)  

        stock.product_name = request.POST.get("product_name")
        stock.quantity = int(request.POST.get("quantity"))
        stock.unit_cost = Decimal(request.POST.get("unit_cost"))   
        stock.selling_price = Decimal(request.POST.get("selling_price"))  
        stock.category = request.POST.get("category")
        stock.supplier = supplier   
        stock.payment_method = request.POST.get("payment_method")
        stock.is_paid = request.POST.get("is_paid") == "on"
        stock.credit_due_date = request.POST.get("credit_due_date") or None

        stock.save()
        return redirect('stock_list')

    return render(request, "edit_stock.html", {
        'stock': stock,
        'suppliers': suppliers
    })


@login_required
def stock_dashboard(request):
    stocks = Stock.objects.all()
    total_value = sum(item.quantity * item.unit_cost for item in stocks)
    low_stock = stocks.filter(quantity__lt=10)
    recent_stocks = stocks
    
    context = {
        "total_value":total_value,
        "low_stock":low_stock,
        "stocks":recent_stocks
         
    }
    return render(request,"stock_dashboard.html", context)


@login_required
def stock_details(request, pk):
    stock = get_object_or_404(Stock, pk=pk)

    context = {
        "stock": stock
    }
    return render(request, "stock_details.html", context)


## for all suppliers
@login_required
def supplier_list(request):
    all_suppliers = Supplier.objects.all()
    context = {
        'suppliers':all_suppliers
    }
    return render (request, "supplier_list.html", context)


@login_required
def add_supplier(request):
     if request.method == "POST":
        payload = request.POST
        sent_name = payload.get("name")
        sent_email =  payload.get("email")
        sent_contact = payload.get("contact")
        sent_address =  payload.get("address")

        # for validating ugandan phone numbers
        phone_pattern = r'^(\+256|256|0)7\d{8}$'

        if not re.match(phone_pattern, sent_contact):
            messages.error(request, "Enter a valid Ugandan phone number")

            context = {
                "form_data":payload
            }
            return render(request,"add_supplier.html",context)
        
        
        newSupplier = Supplier()
        newSupplier.name = sent_name
        newSupplier.email = sent_email
        newSupplier.contact = sent_contact
        newSupplier.address = sent_address
        newSupplier.save()
        messages.success(request, "Supplier added successfully")

        return redirect('supplier_list')
     return render(request,"add_supplier.html")


@login_required
def edit_supplier(request,pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.name = request.POST.get("name")
        supplier.email = request.POST.get("email")
        supplier.contact = request.POST.get("contact")
        supplier.address = request.POST.get("address")
        
        supplier.save()
        return redirect('supplier_list')

    return render(request,"edit_supplier.html", {'supplier':supplier})


@login_required
def delete_supplier(request,pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect('supplier_list')


# For supplier credit 
@login_required
def supplier_credit_list(request):

    credits = SupplierCredit.objects.all().order_by('-id')

    total_credit = SupplierCredit.objects.aggregate(
        total=Sum('amount_owed')
    )['total'] or 0

    total_paid = SupplierCredit.objects.aggregate(
        total=Sum('amount_paid')
    )['total'] or 0

    total_balance = total_credit - total_paid

    context = {
        "credits": credits,
        "total_credit": total_credit,
        "total_paid": total_paid,
        "total_balance": total_balance,
    }

    return render( request, "supplier_credit_list.html", context)


@login_required
def add_supplier_credit(request):

    suppliers = Supplier.objects.all()
    stocks = Stock.objects.all()

    if request.method == "POST":

        supplier = Supplier.objects.get(
            id=request.POST.get("supplier")
        )

        stock = Stock.objects.get(
            id=request.POST.get("stock")
        )

        amount_owed = Decimal(
            request.POST.get("amount_owed")
        )

        amount_paid = Decimal(
            request.POST.get("amount_paid") or 0
        )

        due_date = request.POST.get("due_date")

        SupplierCredit.objects.create(
            supplier=supplier,
            stock=stock,
            amount_owed=amount_owed,
            amount_paid=amount_paid,
            due_date=due_date
        )

        return redirect('supplier_credit_list')

    context = {
        "suppliers": suppliers,
        "stocks": stocks
    }

    return render( request, "add_supplier_credit.html", context)


@login_required
def pay_supplier_credit(request, credit_id):

    credit = get_object_or_404(
        SupplierCredit,
        id=credit_id
    )

    if request.method == "POST":

        payment = Decimal(
            request.POST.get("payment")
        )

        credit.amount_paid += payment

        credit.save()

        return redirect('supplier_credit_list')

    context = {
        "credit": credit
    }

    return render( request, "pay_supplier_credit.html", context)


@login_required
def supplier_credit_detail(request, credit_id):

    credit = get_object_or_404(
        SupplierCredit,
        id=credit_id
    )

    context = {
        "credit": credit
    }

    return render( request, "supplier_credit_detail.html", context)


## functions handling customers
@login_required
def customer_list(request):
    all_customers = Customer.objects.all()
    context = {
        'customers':all_customers
    }
    return render(request,"customer_list.html", context)


@login_required
def add_customer(request):
    if request.method == "POST":
        payload = request.POST
        sent_name = payload.get("name")
        sent_contact = payload.get("contact")
        sent_email = payload.get("email")
        sent_address = payload.get("address")
        sent_nin = payload.get("nin").upper()
        sent_is_credit_customer = payload.get("is_credit_customer") == "on"

        # for validating ugandan phone numbers
        phone_pattern = r'^(\+256|256|0)7\d{8}$'

        # for validating ugandan NIN
        nin_pattern = r'^C[FM][A-Z0-9]{12}$'

        # for phone validation
        if not re.match(phone_pattern, sent_contact):
            messages.error(request, "Enter a valid Ugandan phone number")

            context = {
                "form_data":payload
            }
            return render(request,"add_customer.html",context)
        
        # for NIN validation
        if not re.match(nin_pattern, sent_nin):
            messages.error(request, "Enter a valid Ugandan NIN")

            context = {
                "form_data":payload
            }
            return render(request,"add_customer.html", context)


        newCustomer = Customer()
        newCustomer.name = sent_name
        newCustomer.contact = sent_contact
        newCustomer.email = sent_email
        newCustomer.address = sent_address
        newCustomer.nin = sent_nin
        newCustomer.is_credit_customer = sent_is_credit_customer
        newCustomer.save()
        
        messages.success(request, "Customer added successfully")
        return redirect('customer_list')
    
    return render(request,"add_customer.html")


@login_required
def edit_customer(request,pk):
    customer = get_object_or_404(Customer,pk=pk)
    if request.method == "POST":
        
         
        phone_pattern = r'^(\+256|256|0)7\d{8}$'
        nin_pattern = r'^C[FM][A-Z0-9]{12}$'
        sent_contact = request.POST.get("contact")
        sent_nin = request.POST.get("nin").upper()

        # phone number validation
        if not re.match(phone_pattern, sent_contact):
            messages.error(request, "Enter a valid Ugandan phone number")
            context = {
                "form_data":request.POST,
                "customer":customer
            }
            return render(request, "edit_customer.html", context)
        
         # nin validation
        if not re.match(nin_pattern, sent_nin):
            messages.error(request, "Enter a valid Ugandan NIN (CF or CM only)")

            context = {
                "form_data":request.POST,
                "customer":customer
            }
            return render(request, "edit_customer.html", context)

        customer.name = request.POST.get("name")
        customer.email = request.POST.get("email")
        customer.contact = sent_contact
        customer.address = request.POST.get("address")
        customer.nin = sent_nin
        customer.is_credit_customer = request.POST.get("is_credit_customer") == "on"
        customer.save()
        messages.success(request, "Customer updated successfully")

        return redirect('customer_list')
    return render(request,"edit_customer.html", {'customer':customer})


@login_required
def delete_customer(request,pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')



## Functions handling sales
@login_required
def sale_list(request):
    all_sales = Sale.objects.all()
    context = {
        "sales":all_sales
    }
    return render(request,"sale_list.html", context )


@login_required
def add_sale(request):
    customers = Customer.objects.all()
    stocks = Stock.objects.all()
    

    if request.method == "POST":
        customer = Customer.objects.get(id=request.POST["customer"])
        product = Stock.objects.get(id=request.POST["product"])
        sent_is_fully_paid = request.POST.get("is_fully_paid") == "on"

        quantity_sold = int(request.POST.get("quantity_sold"))

        # VALIDATE STOCK
        if quantity_sold > product.quantity:
            messages.error( request, f"Only {product.quantity} items available.")
            return redirect("add_sale")


        newSale = Sale()
        newSale.customer = customer
        newSale.payment_method = request.POST.get("payment_method")
        newSale.product = product
        newSale.sale_date = request.POST.get("sale_date") or None
        newSale.due_date = request.POST.get("due_date") or None
        newSale.sold_by = request.POST.get("sold_by")
        newSale.distance_km = Decimal(request.POST.get("distance_km") or 0)

        # SET QUANTITY (after validation)
        newSale.quantity_sold = quantity_sold

    # GET PRICES FROM STOCK MODEL (IMPORTANT)
        newSale.unit_selling_price = product.selling_price
        newSale.unit_cost_price = product.unit_cost
        newSale.notes = request.POST.get("notes")

        
        newSale.amount_paid = Decimal(request.POST.get("amount_paid") or 0)

        total_amount = newSale.quantity_sold * newSale.unit_selling_price

    
        if newSale.distance_km <= 10 and total_amount >= 500000:
            newSale.transport_fee = 0
        else:
            newSale.transport_fee = 30000

        
        newSale.save()

        # update payment
        if sent_is_fully_paid:
            newSale.amount_paid = newSale.final_total
            newSale.balance_due = 0
            newSale.is_fully_paid = True

        
        else:
            newSale.balance_due = newSale.final_total - newSale.amount_paid

            
            if newSale.balance_due <= 0:
                newSale.is_fully_paid = True
                newSale.balance_due = 0
            else:
                newSale.is_fully_paid = False

        newSale.save()

        return redirect('sale_list')

    context = {
        "customers": customers,
        "stocks": stocks
    }

    return render(request, "add_sale.html", context)

# For updating a sale
@login_required
def edit_sale(request,pk):
    sale = get_object_or_404(Sale,pk=pk)
    customers = Customer.objects.all()
    stocks = Stock.objects.all()
    
    if request.method == "POST":
        sale.customer = Customer.objects.get(id=request.POST ["customer"])
        sale.product = Stock.objects.get(id=request.POST["product"])
        sale.quantity_sold = int(request.POST.get("quantity_sold"))
        sale.unit_selling_price = Decimal(request.POST.get("unit_selling_price"))
        sale.unit_cost_price = Decimal(request.POST.get("unit_cost_price"))
        total_amount = (sale.quantity_sold * sale.unit_selling_price)
        sale.distance_km = Decimal(request.POST.get("distance_km"))
        sale.payment_method = request.POST.get("payment_method")
        sale.sold_by = request.POST.get("sold_by")
        sale.sale_date = request.POST.get("sale_date") or sale.sale_date
        sale.due_date = request.POST.get("due_date") or None
        sale.amount_paid = Decimal(request.POST.get("amount_paid"))
        sale.notes = request.POST.get("notes")
        sale.is_fully_paid = request.POST.get("is_fully_paid") == "on"
        if sale.distance_km <= 10 and total_amount >= 500000:
            sale.transport_fee = 0
        else:
            sale.transport_fee = 30000

        sale.save()
        return redirect('sale_list')
    context = {
        "customers":customers,
        "stocks":stocks,
        "sale":sale
    }

    return render(request,"edit_sale.html", context)


@login_required
def sale_dashboard(request):
    all_sale = Sale.objects.all()
    recent_sales = Sale.objects.all().order_by('-sale_date')[:10]
    current_date = datetime.date.today()
    total_revenue = Sale.objects.aggregate(
        total=Sum('final_total')
    )['total'] or 0

    total_transport = Sale.objects.aggregate(
        total=Sum('transport_fee')
    )['total'] or 0
    sales_date = timezone.now().date()
    today_sales = Sale.objects.filter(
    sale_date__date=sales_date
    ).aggregate(
    total=Sum('final_total')
    )['total'] or 0


    total_transactions = Sale.objects.aggregate(
        total=Count('id')
    )['total'] or 0

    best_selling = (
    Sale.objects
    .values('product__product_name')
    .annotate(total_sold=Sum('quantity_sold'))
    .order_by('-total_sold')
    .first()
    )

    top_products = (
    Sale.objects
    .values('product__product_name')
    .annotate(
        total_sold=Sum('quantity_sold'),
        total_revenue=Sum('final_total')
    )
    .order_by('-total_sold')[:5]
)

    total_profit = 0 
    for sale in all_sale:
        total_profit += Decimal(sale.profit)
    quantity_sold = Sale.objects.aggregate(total=Sum('quantity_sold'))['total'] or 0

    context = {
        "current_date": current_date,
        "recent_sales":recent_sales,
        "total_transactions":total_transactions,
        "total_profit":total_profit,
        "total_transport":total_transport,
        "quantity_sold":quantity_sold,
        "date":current_date,
        "total_revenue":total_revenue,
        "total_sales_today": today_sales,
        "best_selling":best_selling,
        "top_products":top_products
    }
    # print(context)
    return render(request,"sale_dashboard.html", context)


@login_required
def credit_list(request):
    credit_sales = Sale.objects.filter(is_fully_paid = False)
    context = {
        "credit_sales":credit_sales,
        "today":datetime.date.today()
    }
    return render(request, "customer_credit_list.html", context)


@login_required
def sale_details(request,pk):
    sale = get_object_or_404(Sale,pk=pk)
    context ={
        "sale":sale
    }
    return render(request,"sale_details.html",context)


@login_required
def sale_receipt(request, pk):
    sales = get_object_or_404(Sale, pk=pk)
    context = {
        "sale": sales,
        "receipt_type": "sale"
    }
    return render(request, "sale_receipt.html", context)


@login_required
def payment(request):
    return render(request, "payment.html")


@login_required
def add_payment(request):
    sales = Sale.objects.all()

    if request.method == "POST":

        sale = Sale.objects.get(
            id=request.POST.get("sale")
        )

        # for creating  a payment
        payment = Payment()
        payment.sale = sale
        payment.amount = Decimal(request.POST.get("amount"))
        payment.method = request.POST.get("method")
        payment.save()

        #  for recalculating data  from the database 
        total_paid = Payment.objects.filter(sale=sale).aggregate(
        total=Sum('amount'))['total'] or Decimal("0")
        sale.amount_paid = total_paid

        # for checking and updating the balance_due
        sale.balance_due = sale.final_total - sale.amount_paid
        if sale.balance_due <= 0:
            sale.is_fully_paid = True
            sale.balance_due = 0
        else:
            sale.is_fully_paid = False
        sale.save()

    
        # for automatically adding the payment into the deposit dashboard
        newDeposit = Deposit()
        newDeposit.customer_name = sale.customer
        newDeposit.amount = payment.amount
        newDeposit.sale = sale
        newDeposit.payment_method = payment.method
        newDeposit.save()

        # update sale payment info
        sale.amount_paid += payment.amount

        sale.balance_due = sale.final_total - sale.amount_paid

        if sale.balance_due <= 0:
            sale.balance_due = 0
            sale.is_fully_paid = True
        else:
            sale.is_fully_paid = False

        sale.save()

        return redirect('payment_history')

    context = {
        "sales": sales
    }

    return render(request, "add_payment.html", context)


@login_required
def payment_history(request):
    payments = Payment.objects.all().order_by(
        '-payment_date'
    )

    latest_payment = payments.first()

    context = {
        "payments": payments,
        "latest_payment": latest_payment
    }

    return render(
        request,
        "payment_history.html",
        context
    )


@login_required
def deposit_receipt(request, pk):
    deposit = get_object_or_404(Deposit, pk=pk)

    sale = deposit.sale
    sale_total = sale.final_total or Decimal('0')
    paid_amount = sale.amount_paid or Decimal('0')

    balance = sale_total - paid_amount
    context = {
        "deposit": deposit,
        "sale": sale,
        "balance": balance,
        "sale_total": sale_total,
        "paid_amount": paid_amount,
    }

    return render(request, "deposit_receipt.html", context)

   
@login_required
def deposit_list(request):

    all_deposits = Deposit.objects.all()

    total_amount = all_deposits.aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    customer_count = all_deposits.values(
        "customer_name"
    ).distinct().count()

    context = {
        "deposits": all_deposits,
        "total_amount": total_amount,
        "customer_count": customer_count
    }

    return render(
        request,
        "deposit_list.html",
        context
    )


@login_required
def edit_deposit(request, pk):

    deposit = get_object_or_404(Deposit,pk=pk)

    customers = Customer.objects.all()

    sales = Sale.objects.all()
    sales = [sale for sale in sales if sale.final_total > sale.amount_paid]
    for sale in sales:
        sale.balance = sale.final_total - sale.amount_paid


    if request.method == "POST":

        deposit.customer_name = Customer.objects.get(id=request.POST["customer_name"])
        
        deposit.sale = Sale.objects.get(
            id=request.POST["sale"]
        )

        deposit.amount = Decimal( request.POST.get("amount"))

        deposit.payment_method = request.POST.get("payment_method")

        deposit.save()

        return redirect('deposit_list')

    context = {
        "deposit": deposit,
        "customers": customers,
        "sales":sales
    }

    return render(request,"edit_deposit.html",context)


@login_required
def admin_dashboard(request):
    total_sales = Sale.objects.aggregate(Sum("final_total"))["final_total__sum"] or 0
    total_payments = Payment.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    total_deposits = Deposit.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    customers = Customer.objects.count()
    recent_sales = Sale.objects.all().order_by("-id")[:5]
    # recent_payments = Payment.objects.all().order_by("-payment_date")[:5]
    recent_deposits = Deposit.objects.all().order_by("-date")[:5]
    
    context = {
        "total_sales":total_sales,
        "total_payments":total_payments,
        "total_deposits":total_deposits,
        "customers":customers,
        "recent_sales":recent_sales,
        # "recent_payments":recent_payments,
        "recent_deposits":recent_deposits
    }

    return render(request, "admin_dashboard.html", context)


@login_required
def reports_dashboard(request):
    # for date range filter (default = last 30 days)
    period = request.GET.get('period', '30')
    days = int(period)
    start_date = timezone.now() - timedelta(days=days)

    # for sales summary 
    sales= Sale.objects.filter(sale_date__gte=start_date)
    total_sales = sales.aggregate(total=Sum('final_total'))['total'] or 0
    total_transactions = sales.count()

    # for stock summary
    low_stock_items = Stock.objects.filter(quantity__lte=10)
    total_stock_value = Stock.objects.aggregate(value=Sum('quantity') * Sum('unit_cost'))['value'] or 0

    # for supplier credit 
    total_credit = SupplierCredit.objects.aggregate(total=Sum('amount_owed'))['total'] or 0
    over_due_credit = SupplierCredit.objects.filter(due_date__lte=timezone.now(), is_cleared=False)

    # for deposit scheme
    total_deposits = Deposit.objects.aggregate(total=Sum('amount'))['total'] or 0
    active_depositors = Deposit.objects.values('customer_name').distinct().count()

    context = {
        'period': period,
        'total_sales': total_sales,
        'total_transactions': total_transactions,
        'low_stock_items': low_stock_items,
        'total_credit': total_credit,
        'overdue_credit': over_due_credit,
        'total_deposits': total_deposits,
        'total_stock_value':total_stock_value,
        'active_depositors': active_depositors,
        'sales_by_day': sales.values('sale_date__date').annotate(total=Sum('final_total')).order_by('sale_date__date'),
    }
    return render(request, 'reports_dashboard.html', context)



