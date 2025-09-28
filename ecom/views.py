from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Order, OrderItem
from .serializers import ProductSerializer, OrderSerializer
from rewards.permissions import IsAdminUser, IsRegularUser
from rewards.models import PointsRate

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': 'Order cannot be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'confirmed'
        order.save()
        # Points awarded in model save()
        active_rate = PointsRate.objects.filter(active=True).first()
        points_awarded = int(round(order.total_price * (active_rate.rate if active_rate else 1.0)))
        return Response({'message': f'Order confirmed, {points_awarded} points awarded'})
