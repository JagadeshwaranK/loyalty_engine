from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('user', 'User'),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

# class User(AbstractUser):
#     tier = models.CharField(max_length=20, default='Bronze')
#     points = models.IntegerField(default=0)

#     def __str__(self):
#         return self.username

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    tier = models.CharField(max_length=20, default='Bronze')
    points = models.IntegerField(default=0)
    loyalty_opt_in = models.BooleanField(default=False, help_text="User has opted into the loyalty program")

    def __str__(self):
        return self.username

class Reward(models.Model):
    REDEMPTION_TYPE_CHOICES = [
        ('amount_discount', 'Amount Discount'),
        ('free_product', 'Free Product'),
        ('free_shipping', 'Free Shipping'),
    ]

    name = models.CharField(max_length=100)
    points_required = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    redemption_type = models.CharField(max_length=20, choices=REDEMPTION_TYPE_CHOICES, default='amount_discount')
    amount_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    free_product_sku = models.CharField(max_length=100, null=True, blank=True)
    free_shipping = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_bonus = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Redemption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    coupon_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} redeemed {self.reward.name} at {self.redeemed_at}"

class PointsRate(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Points per dollar (e.g., 5.00 for 5 points per $1)")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Points Rate: {self.rate} points per dollar"

    class Meta:
        verbose_name = "Points Rate"
        verbose_name_plural = "Points Rates"

AUTH_USER_MODEL = 'rewards.User'
