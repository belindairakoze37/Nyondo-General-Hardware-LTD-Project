from django import forms
from decimal import Decimal
import re

from .models import Customer, Sale, Stock, Supplier, SupplierCredit


class SupplierForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Supplier
        fields = ["name", "email", "contact", "address"]
        error_messages = {
            "name": {
                "required": "Supplier name is required.",
            },
            "email": {
                "required": "Email address is required.",
                "invalid": "Enter a valid email address.",
            },
            "contact": {
                "required": "Contact number is required.",
            },
            "address": {
                "required": "Address is required.",
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter supplier name"}),
            "email": forms.TextInput(attrs={"placeholder": "supplier@example.com"}),
            "contact": forms.TextInput(attrs={
                "maxlength": "13",
                "placeholder": "+25677567890",
            }),
            "address": forms.Textarea(attrs={"placeholder": "Enter full address"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Supplier name is required.")
        return name

    def clean_contact(self):
        contact = self.cleaned_data["contact"].strip()
        phone_pattern = r'^(\+256|256|0)7\d{8}$'
        if not re.match(phone_pattern, contact):
            raise forms.ValidationError("Enter a valid Ugandan phone number.")
        return contact

    def clean_address(self):
        address = self.cleaned_data["address"].strip()
        if not address:
            raise forms.ValidationError("Address is required.")
        return address


class SupplierCreditForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = SupplierCredit
        fields = ["supplier", "stock", "amount_owed", "amount_paid", "due_date"]
        error_messages = {
            "supplier": {
                "required": "Supplier is required.",
            },
            "stock": {
                "required": "Stock/product is required.",
            },
            "amount_owed": {
                "required": "Amount owed is required.",
                "invalid": "Enter a valid amount owed.",
            },
            "amount_paid": {
                "invalid": "Enter a valid amount paid.",
            },
            "due_date": {
                "required": "Due date is required.",
                "invalid": "Enter a valid due date.",
            },
        }
        widgets = {
            "amount_owed": forms.TextInput(attrs={
                "inputmode": "decimal",
                "placeholder": "Enter amount owed",
            }),
            "amount_paid": forms.TextInput(attrs={
                "inputmode": "decimal",
                "placeholder": "Enter amount paid",
            }),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].empty_label = "Select Supplier"
        self.fields["stock"].empty_label = "Select Product"
        self.fields["amount_paid"].required = False
        if not self.is_bound:
            self.fields["amount_paid"].initial = Decimal("0")

    def clean_amount_owed(self):
        amount_owed = self.cleaned_data["amount_owed"]
        if amount_owed <= Decimal("0"):
            raise forms.ValidationError("Amount owed must be greater than 0.")
        return amount_owed

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data.get("amount_paid") or Decimal("0")
        if amount_paid < Decimal("0"):
            raise forms.ValidationError("Amount paid cannot be negative.")
        return amount_paid

    def clean(self):
        cleaned_data = super().clean()
        amount_owed = cleaned_data.get("amount_owed")
        amount_paid = cleaned_data.get("amount_paid")

        if (
            amount_owed is not None and
            amount_paid is not None and
            amount_paid > amount_owed
        ):
            self.add_error(
                "amount_paid",
                "Amount paid cannot be greater than amount owed.",
            )

        return cleaned_data


class SupplierCreditPaymentForm(forms.Form):
    use_required_attribute = False

    payment = forms.DecimalField(
        error_messages={
            "required": "Payment amount is required.",
            "invalid": "Enter a valid payment amount.",
        },
        widget=forms.TextInput(attrs={
            "inputmode": "decimal",
            "placeholder": "Enter payment amount",
        }),
    )

    def __init__(self, *args, credit=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.credit = credit

    def clean_payment(self):
        payment = self.cleaned_data["payment"]
        if payment <= Decimal("0"):
            raise forms.ValidationError("Payment amount must be greater than 0.")

        if self.credit and payment > self.credit.balance:
            raise forms.ValidationError(
                "Payment amount cannot be greater than the remaining balance."
            )

        return payment


class AddSaleForm(forms.Form):
    use_required_attribute = False

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        empty_label="Select Customer",
        error_messages={"required": "Customer is required."},
    )
    product = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        empty_label="Select Product",
        error_messages={"required": "Product is required."},
    )
    unit_selling_price = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            "readonly": "readonly",
            "placeholder": "Auto-filled from stock",
        }),
    )
    unit_cost_price = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            "readonly": "readonly",
            "placeholder": "Auto-filled from stock",
        }),
    )
    quantity_sold = forms.IntegerField(
        error_messages={
            "required": "Quantity sold is required.",
            "invalid": "Enter a valid quantity.",
        },
        widget=forms.TextInput(attrs={
            "id": "quantity-sold",
            "inputmode": "numeric",
            "placeholder": "e.g., 5",
        }),
    )
    payment_method = forms.ChoiceField(
        choices=Sale.PAYMENT_METHOD_CHOICES,
        error_messages={"required": "Payment method is required."},
    )
    distance_km = forms.DecimalField(
        required=False,
        initial=Decimal("0"),
        error_messages={"invalid": "Enter a valid distance."},
        widget=forms.TextInput(attrs={
            "inputmode": "decimal",
            "placeholder": "Additional delivery cost",
        }),
    )
    amount_paid = forms.DecimalField(
        required=False,
        initial=Decimal("0"),
        error_messages={"invalid": "Enter a valid amount paid."},
        widget=forms.TextInput(attrs={
            "inputmode": "decimal",
            "placeholder": "Partial or full payment",
        }),
    )
    due_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%d"],
        error_messages={"invalid": "Enter a valid due date."},
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    is_fully_paid = forms.BooleanField(required=False)
    sold_by = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Salesperson name"}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            "placeholder": "Special instructions, discount, comments...",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.all()
        self.fields["product"].queryset = Stock.objects.all()
        self.fields["product"].label_from_instance = (
            lambda stock: f"{stock.product_name} ({stock.quantity} available)"
        )

    def clean_quantity_sold(self):
        quantity_sold = self.cleaned_data["quantity_sold"]
        if quantity_sold < 1:
            raise forms.ValidationError("Quantity sold must be at least 1.")
        return quantity_sold

    def clean_distance_km(self):
        distance_km = self.cleaned_data.get("distance_km") or Decimal("0")
        if distance_km < Decimal("0"):
            raise forms.ValidationError("Distance cannot be negative.")
        return distance_km

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data.get("amount_paid") or Decimal("0")
        if amount_paid < Decimal("0"):
            raise forms.ValidationError("Amount paid cannot be negative.")
        return amount_paid

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        quantity_sold = cleaned_data.get("quantity_sold")

        if product and quantity_sold and quantity_sold > product.quantity:
            self.add_error(
                "quantity_sold",
                f"Only {product.quantity} items available.",
            )

        return cleaned_data


class EditSaleForm(forms.Form):
    use_required_attribute = False

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        empty_label="Select Customer",
        error_messages={"required": "Customer is required."},
    )
    product = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        empty_label="Select Product",
        error_messages={"required": "Product is required."},
    )
    quantity_sold = forms.IntegerField(
        error_messages={
            "required": "Quantity sold is required.",
            "invalid": "Enter a valid quantity.",
        },
        widget=forms.TextInput(attrs={
            "inputmode": "numeric",
            "placeholder": "e.g., 5",
        }),
    )
    unit_selling_price = forms.DecimalField(
        error_messages={
            "required": "Unit selling price is required.",
            "invalid": "Enter a valid selling price.",
        },
        widget=forms.TextInput(attrs={
            "placeholder": "UGX 0.00",
        }),
    )
    unit_cost_price = forms.DecimalField(
        error_messages={
            "required": "Unit cost price is required.",
            "invalid": "Enter a valid cost price.",
        },
        widget=forms.TextInput(attrs={
            "placeholder": "UGX 0.00",
        }),
    )
    payment_method = forms.ChoiceField(
        choices=Sale.PAYMENT_METHOD_CHOICES,
        error_messages={"required": "Payment method is required."},
    )
    distance_km = forms.DecimalField(
        required=False,
        initial=Decimal("0"),
        error_messages={"invalid": "Enter a valid distance."},
        widget=forms.TextInput(attrs={
            "inputmode": "decimal",
            "placeholder": "Additional delivery cost",
        }),
    )
    amount_paid = forms.DecimalField(
        required=False,
        initial=Decimal("0"),
        error_messages={"invalid": "Enter a valid amount paid."},
        widget=forms.TextInput(attrs={
            "inputmode": "decimal",
            "placeholder": "Partial or full payment",
        }),
    )
    sale_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%d"],
        error_messages={"invalid": "Enter a valid sale date."},
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    due_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%d"],
        error_messages={"invalid": "Enter a valid due date."},
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    is_fully_paid = forms.BooleanField(required=False)
    sold_by = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Salesperson name"}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            "placeholder": "Special instructions, discount, comments...",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.all()
        self.fields["product"].queryset = Stock.objects.all()
        self.fields["product"].label_from_instance = (
            lambda stock: f"{stock.product_name} ({stock.quantity} available)"
        )

    def clean_quantity_sold(self):
        quantity_sold = self.cleaned_data["quantity_sold"]
        if quantity_sold < 1:
            raise forms.ValidationError("Quantity sold must be at least 1.")
        return quantity_sold

    def clean_unit_selling_price(self):
        unit_selling_price = self.cleaned_data["unit_selling_price"]
        if unit_selling_price <= Decimal("0"):
            raise forms.ValidationError("Unit selling price must be greater than 0.")
        return unit_selling_price

    def clean_unit_cost_price(self):
        unit_cost_price = self.cleaned_data["unit_cost_price"]
        if unit_cost_price <= Decimal("0"):
            raise forms.ValidationError("Unit cost price must be greater than 0.")
        return unit_cost_price

    def clean_distance_km(self):
        distance_km = self.cleaned_data.get("distance_km") or Decimal("0")
        if distance_km < Decimal("0"):
            raise forms.ValidationError("Distance cannot be negative.")
        return distance_km

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data.get("amount_paid") or Decimal("0")
        if amount_paid < Decimal("0"):
            raise forms.ValidationError("Amount paid cannot be negative.")
        return amount_paid


class StockForm(forms.ModelForm):
    use_required_attribute = False

    PRODUCT_CHOICES = [
        ("", "-- Select Product --"),
        ("Cement - CEM II N", "Cement - CEM II N"),
        ("Cement - CEM III N", "Cement - CEM III N"),
        ("Iron Bar - 10mm", "Iron Bar - 10mm"),
        ("Iron Bar - 12mm", "Iron Bar - 12mm"),
        ("Iron Bar - 16mm", "Iron Bar - 16mm"),
        ("Nails - 1 inch", "Nails - 1 inch"),
        ("Nails - 3 inch", "Nails - 3 inch"),
        ("Nails - 4 inch", "Nails - 4 inch"),
        ("Nails - 5 inch", "Nails - 5 inch"),
        ("Roofing Nails", "Roofing Nails"),
        ("Wheelbarrow", "Wheelbarrow"),
        ("Wire Mesh", "Wire Mesh"),
        ("Barbed Wire - High Tensile", "Barbed Wire - High Tensile"),
        ("Barbed Wire - Low Tensile", "Barbed Wire - Low Tensile"),
        ("Iron Sheets - Green", "Iron Sheets - Green"),
        ("Iron Sheets - Blue", "Iron Sheets - Blue"),
        ("Iron Sheets - Red", "Iron Sheets - Red"),
        ("Iron Sheets - White", "Iron Sheets - Silver"),
    ]

    product_name = forms.ChoiceField(
        choices=PRODUCT_CHOICES,
        error_messages={"required": "Product name is required."},
    )

    class Meta:
        model = Stock
        fields = [
            "product_name",
            "quantity",
            "unit_cost",
            "selling_price",
            "category",
            "supplier",
            "payment_method",
            "is_paid",
            "credit_due_date",
            "unit",
        ]
        error_messages = {
            "quantity": {
                "required": "Quantity is required.",
                "invalid": "Enter a valid quantity.",
            },
            "unit_cost": {
                "required": "Unit cost is required.",
                "invalid": "Enter a valid unit cost.",
            },
            "selling_price": {
                "required": "Selling price is required.",
                "invalid": "Enter a valid selling price.",
            },
            "category": {
                "required": "Category is required.",
            },
            "supplier": {
                "required": "Supplier is required.",
            },
            "payment_method": {
                "required": "Payment method is required.",
            },
            "unit": {
                "required": "Unit of measure is required.",
            },
        }
        widgets = {
            "quantity": forms.TextInput(attrs={
                "inputmode": "numeric",
                "placeholder": "Enter quantity",
            }),
            "unit_cost": forms.TextInput(attrs={
                "inputmode": "decimal",
                "placeholder": "Cost from supplier",
            }),
            "selling_price": forms.TextInput(attrs={
                "inputmode": "decimal",
                "placeholder": "Price to customers",
            }),
            "credit_due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = None
        self.fields["category"].choices = [("", "-- Select Category --")] + list(
            Stock.CATEGORY_CHOICES
        )
        self.fields["supplier"].empty_label = "-- Select Supplier --"
        self.fields["payment_method"].choices = [
            ("", "-- Select Payment Method --")
        ] + list(Stock.PAYMENT_METHOD_CHOICES)
        self.fields["unit"].choices = [
            ("", "-- Select Unit of Measure --")
        ] + list(Stock.UNIT_CHOICES)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity

    def clean_unit_cost(self):
        unit_cost = self.cleaned_data["unit_cost"]
        if unit_cost <= Decimal("0"):
            raise forms.ValidationError("Unit cost must be greater than 0.")
        return unit_cost

    def clean_selling_price(self):
        selling_price = self.cleaned_data["selling_price"]
        if selling_price <= Decimal("0"):
            raise forms.ValidationError("Selling price must be greater than 0.")
        return selling_price
