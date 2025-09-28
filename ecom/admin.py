from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    raw_id_fields = ['user']

admin.site.register(OrderItem)
