from django.utils import timezone
from django.shortcuts import render,redirect,get_object_or_404
from web.models import Supplier
from web.models import Stock
from web.models import Sale
from web.models import Customer
from web.models import Payment
from web.models import Deposit
from decimal import Decimal
import datetime
from django.db.models import Sum, Count

# Create your views here.

## functions handling stock 

def index(request):
    return render(request,"index.html")
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



def stock_dashboard(request):
    stocks = Stock.objects.all()
    total_products = stocks.count()
    total_quantity = sum(item.quantity for item in stocks)
    total_value = sum(item.quantity * item.unit_cost for item in stocks)
    low_stock = stocks.filter(quantity__lt=10)
    recent_stocks = stocks
    
    context = {
        "total_products":total_products,
        "total_quantity":total_quantity,
        "total_value":total_value,
        "low_stock":low_stock,
        "stocks":recent_stocks
         
    }
    return render(request,"stock_dashboard.html", context)

def stock_details(request, pk):
    stock = get_object_or_404(Stock, pk=pk)

    context = {
        "stock": stock
    }
    return render(request, "stock_details.html", context)

## functions handling suppliers
def supplier_list(request):
    all_suppliers = Supplier.objects.all()
    context = {
        'suppliers':all_suppliers
    }
    return render (request, "supplier_list.html", context)

def add_supplier(request):
     if request.method == "POST":
        payload = request.POST
        sent_name = payload.get("name")
        sent_email =  payload.get("email")
        sent_contact = payload.get("contact")
        sent_address =  payload.get("address")
        
        newSupplier = Supplier()
        newSupplier.name = sent_name
        newSupplier.email = sent_email
        newSupplier.contact = sent_contact
        newSupplier.address = sent_address
        newSupplier.save()
        return redirect('supplier_list')
     return render(request,"add_supplier.html")

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

def delete_supplier(request,pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect('supplier_list')

def login(request):
    return render(request,"login.html")

## functions handling customers
def customer_list(request):
    all_customers = Customer.objects.all()
    context = {
        'customers':all_customers
    }
    return render(request,"customer_list.html", context)

def add_customer(request):
    if request.method == "POST":
        payload = request.POST
        sent_name = payload.get("name")
        sent_contact = payload.get("contact")
        sent_email = payload.get("email")
        sent_address = payload.get("address")
        sent_nin = payload.get("nin")
        sent_distance_km = int(payload.get("distance_km") or 0) 
        sent_is_credit_customer = payload.get("is_credit_customer") == "on"

        newCustomer = Customer()
        newCustomer.name = sent_name
        newCustomer.contact = sent_contact
        newCustomer.email = sent_email
        newCustomer.address = sent_address
        newCustomer.nin = sent_nin
        newCustomer.distance_km = sent_distance_km
        newCustomer.is_credit_customer = sent_is_credit_customer
        newCustomer.save()
        return redirect('customer_list')
    
    return render(request,"add_customer.html")

def edit_customer(request,pk):
    customer = get_object_or_404(Customer,pk=pk)
    if request.method == "POST":
        customer.name = request.POST.get("name")
        customer.email = request.POST.get("email")
        customer.contact = request.POST.get("contact")
        customer.address = request.POST.get("address")
        customer.distance_km = int(request.POST.get("distance_km"))
        customer.nin = request.POST.get("nin")
        customer.is_credit_customer = request.POST.get("is_credit_customer") == "on"
        customer.save()
        return redirect('customer_list')
    return render(request,"edit_customer.html", {'customer':customer})

def delete_customer(request,pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')

## Functions handling sales
def sale_list(request):
    all_sales = Sale.objects.all()
    context = {
        "sales":all_sales
    }
    return render(request,"sale_list.html", context )

def add_sale(request):
    customers = Customer.objects.all()
    stocks = Stock.objects.all()
    if request.method == "POST":
        customer = Customer.objects.get(id=request.POST["customer"])
        product = Stock.objects.get(id=request.POST["product"])
        sent_is_fully_paid = request.POST.get("is_fully_paid") == "on"

        # creating a new sale
        newSale = Sale()
        newSale.customer = customer
        newSale.payment_method = request.POST.get("payment_method")
        newSale.is_fully_paid = sent_is_fully_paid
        newSale.product = product
        newSale.sale_date = request.POST.get("sale_date") or None
        newSale.due_date = request.POST.get("due_date") or None
        newSale.sold_by = request.POST.get("sold_by")
        newSale.distance_km = int(customer.distance_km)

        newSale.quantity_sold = int(request.POST.get("quantity_sold"))
        newSale.unit_selling_price = Decimal(request.POST.get("unit_selling_price"))
        newSale.unit_cost_price = Decimal(request.POST.get("unit_cost_price"))
        newSale.notes = request.POST.get("notes")
        total_amount = (newSale.quantity_sold * newSale.unit_selling_price)
        if newSale.distance_km <= 10 and total_amount >= 500000:
            newSale.transport_fee = 0
        else:
            newSale.transport_fee = 30000
        newSale.save()
        return redirect('sale_list')
    

    context = {
            "customers": customers,
            "stocks":stocks
        }  
    return render(request, "add_sale.html", context)

# For updating a sale
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
        sale.distance_km = int(sale.customer.distance_km)
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
    }
    # print(context)
    return render(request,"sale_dashboard.html", context)

def credit_list(request):
    credit_sales = Sale.objects.filter(is_fully_paid = False)
    context = {
        "credit_sales":credit_sales,
        "today":datetime.date.today()
    }
    return render(request, "customer_credit_list.html", context)

def sale_details(request,pk):
    sale = get_object_or_404(Sale,pk=pk)
    context ={
        "sale":sale
    }
    return render(request,"sale_details.html",context)

def payment(request):
    return render(request,"payment.html")
def receipt(request,pk):
    sale = get_object_or_404(Sale,pk=pk)
    context = {
        "sale":sale
    }
    return render(request,"receipt.html", context)
def add_payment(request):
    sales = Sale.objects.all()

    if request.method == "POST":
        sale = Sale.objects.get(id=request.POST.get("sale"))

        payment = Payment()
        payment.sale = sale
        payment.amount = Decimal(request.POST.get("amount"))
        payment.method = request.POST.get("method")
        payment.save()

        # for  updating sale amount paid
        sale.amount_paid += payment.amount

        # for checking the  balance
        if sale.amount_paid >= sale.final_total:
            sale.is_fully_paid = True

        sale.save()

        return redirect('payment_history')

    context = {
        "sales": sales
    }

    return render(request, "add_payment.html", context)

def payment_history(request):
    payments = Payment.objects.all().order_by('-payment_date')
    latest_payment = payments.first()
    context = {
        "payments":payments,
        "latest_payment":latest_payment
    }
    return render(request,"payment_history.html", context)

def deposit_list(request):
    all_deposits = Deposit.objects.all()
    total_amount = all_deposits.aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    customer_count = all_deposits.values("customer_name").distinct().count()

    context = {
        "deposits":all_deposits,
        "total_amount":total_amount,
        "customer_count":customer_count
    }
    return render(request, "deposit_list.html", context)

def add_deposit(request):
    customers = Customer.objects.all()
    if request.method == "POST":
        payload = request.POST
        customer_id = request.POST.get("customer_name")
        customer = get_object_or_404(Customer,id=customer_id)
        sent_amount = Decimal(payload.get("amount"))
        sent_payment_method = payload.get("payment_method")
        
        # creating a new deposit 
        newDeposit = Deposit()
        newDeposit.customer_name = customer
        newDeposit.amount = sent_amount
        newDeposit.payment_method = sent_payment_method
        newDeposit.save()
        return redirect('deposit_list')
    return render(request,"add_deposit.html", {"customers":customers} )
    

def edit_deposit(request,pk):
    pass

