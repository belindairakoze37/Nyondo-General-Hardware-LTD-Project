from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import logout

# Create your views here

# This is for registering a new user
def register_user(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("login")
