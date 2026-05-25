from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# Create your views here

# This is for registering a new user
@login_required
def register_user(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # For redirecting users to their respective places
            role = user.profile.role  

            if role == "admin":
                return redirect('admin_dashboard')

            elif role == "store_manager":
                return redirect('stock_dashboard')

            elif role == "sales_attendant":
                return redirect('sale_dashboard')

            

    return render(request, "registration/login.html")


def user_logout(request):
    logout(request)
    return redirect("login")
