from rest_framework import serializers
from .models import Product, Order, OrderItem
from rewards.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = OrderItemSerializer(many=True, write_only=True)
    user = serializers.StringRelatedField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'items_data', 'total_price', 'status', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        validated_data.pop('user', None)
        validated_data.pop('total_price', None)
        user = self.context['request'].user
        order = Order.objects.create(user=user, total_price=0, **validated_data)
        total = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price
            item = OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total += price * quantity
        order.total_price = total
        order.save()
        return order
