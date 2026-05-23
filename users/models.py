from django.db import models
from django.contrib.auth.models import User


# Create your models here
class UserProfile(models.Model):
    ROLE_CHOICES = (("admin", "Admin"), ("sales_attendant", "Sales Attendant"), ("store_manager", "Store Manager"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"{self.user.username} - {self.role}"
