from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

# This model is for tracking  a supplier
class Supplier(models.Model):

    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# This model is for tracking stock
class Stock(models.Model):

    # Category choices
    CATEGORY_CHOICES = [
        ('cement', 'Cement'),
        ('steel', 'Steel / Iron Bars'),
        ('nails', 'Nails'),
        ('hardware', 'Hardware'),
        ('roofing', 'Roofing'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('critical', 'Critical - Below 10 units'),
        ('low', 'Low Stock - Below 30 units'),
        ('normal', 'Normal Stock'),
        ('overstock', 'Overstock'),
    ]

    # Payment method choices
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit', 'Credit (Pay Later)'),
        ('cheque', 'Cheque'),
        ('mobile_money', 'Mobile Money'),
    ]

    # Unit choices
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('bags', 'Bags'),
    ]

    # Basic information
    product_name = models.CharField(max_length=50)

    category = models.CharField(
        max_length=60,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    # Quantity fields
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    minimum_stock_level = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)]
    )

    maximum_stock_level = models.IntegerField(
        default=500,
        validators=[MinValueValidator(0)]
    )

    reorder_quantity = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0)]
    )

    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='pcs'
    )

    # Pricing fields
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Date received
    received_date = models.DateField(auto_now_add=True)

    # Supplier
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True
    )

    # Payment info
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )

    credit_due_date = models.DateField(
        blank=True,
        null=True
    )

    is_paid = models.BooleanField(default=False)

    # Stock status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='normal'
    )

    # Notes
    notes = models.TextField(
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):

        # Automatic stock status updates
        if self.quantity < 10:
            self.status = 'critical'

        elif self.quantity < 30:
            self.status = 'low'

        elif self.quantity > self.maximum_stock_level:
            self.status = 'overstock'

        else:
            self.status = 'normal'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


# This model is for tracking customers who are no credit
class Customer(models.Model):

    name = models.CharField(max_length=100)

    contact = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    nin = models.CharField(
        max_length=20,
        unique=True
    )

    is_credit_customer = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# This model is for tracking a sale made 
class Sale(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit', 'Credit'),
    ]
    product = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True
    )

    quantity_sold = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    unit_selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    unit_cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    final_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    distance_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )

    transport_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    balance_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    due_date = models.DateTimeField(
        blank=True,
        null=True
    )

    is_fully_paid = models.BooleanField(default=False)

    sale_date = models.DateTimeField(auto_now_add=True)

    sold_by = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):


        # Check if new sale
        is_new = self.pk is None
        if is_new:
            if self.quantity_sold > self.product.quantity:
                raise ValidationError( "Not enough stock available")
    
        self.subtotal = (
            self.quantity_sold *
            self.unit_selling_price
        )

        profit_per_unit = (
            self.unit_selling_price -
            self.unit_cost_price
        )

        self.profit = (
            profit_per_unit *
            self.quantity_sold
        )

        self.final_total = (
            self.subtotal +
            self.transport_fee
        )

        self.balance_due = (self.final_total -self.amount_paid)

        self.is_fully_paid = self.balance_due <= 0

        # Save sale first
        super().save(*args, **kwargs)

        # Reduce stock only when creating new sale
        if is_new:
            self.product.quantity -= self.quantity_sold
            self.product.save()

    def __str__(self):
        return f"Sale #{self.id}"


# This model is for tracking payments/ deposits made by a customer 
class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    payment_date = models.DateField(auto_now_add=True)

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):

        # Save payment first
        super().save(*args, **kwargs)

        # Get related sale
        sale = self.sale

        # Calculate total payments
        total_payments = Payment.objects.filter(
            sale=sale
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        # Update sale
        sale.amount_paid = total_payments

        sale.balance_due = (
            sale.final_total -
            total_payments
        )

        sale.is_fully_paid = sale.balance_due <= 0

        sale.save()

    def __str__(self):
        return f"Payment for Sale #{self.sale.id}"


# This is for tracking supplier credit 
class SupplierCredit(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE
    )

    stock = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT
    )

    amount_owed = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    due_date = models.DateField()

    is_cleared = models.BooleanField(default=False)

    @property
    def balance(self):
        return self.amount_owed - self.amount_paid

    def save(self, *args, **kwargs):

        # Auto update clearance status
        self.is_cleared = (
            self.amount_paid >= self.amount_owed
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier.name} Credit"
    
class Deposit(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    customer_name = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.amount}"
    
