from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count, F
from django.utils.timezone import now
from datetime import timedelta
from .models import User, Reward, Redemption
from ecom.models import Order, Product

class AnalyticsDataView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Revenue and orders by month (last 6 months) - using actual orders
        today = now().date()
        six_months_ago = today - timedelta(days=180)
        revenue_by_month = (
            Order.objects.filter(created_at__gte=six_months_ago, status='confirmed')
            .annotate(month=F('created_at__month'))
            .values('month')
            .annotate(
                revenue=Sum('total_price'),
                orders=Count('id')
            )
            .order_by('month')
        )

        # User engagement: active users by hour (mocked for now)
        user_engagement = [
            {'hour': str(h).zfill(2), 'users': h * 10 + 5} for h in range(24)
        ]

        # Product performance: top 5 products by sales and revenue
        product_performance = (
            Product.objects.annotate(
                sales=Sum('orderitem__quantity'),
                revenue=Sum(F('orderitem__quantity') * F('orderitem__price'))
            )
            .order_by('-sales')[:5]
            .values('name', 'sales', 'revenue')
        )

        # Category distribution: count of products by category
        category_distribution = (
            Product.objects.values('category')
            .annotate(value=Count('id'))
            .order_by('-value')
        )

        # User points distribution by tier
        points_distribution = (
            User.objects.values('tier')
            .annotate(users=Count('id'), points=Sum('points'))
            .order_by('tier')
        )

        data = {
            'revenueByMonth': list(revenue_by_month),
            'userEngagement': user_engagement,
            'productPerformance': list(product_performance),
            'categoryDistribution': list(category_distribution),
            'pointsDistribution': list(points_distribution),
        }
        return Response(data)
