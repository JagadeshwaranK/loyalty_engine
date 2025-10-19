from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RewardViewSet, CampaignViewSet,
    RedemptionViewSet, AdminRewardViewSet,
    UserRedemptionViewSet, PointsRateViewSet, MyTokenObtainPairView
)
from .analytics import AnalyticsDataView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'rewards'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'rewards', RewardViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'redemptions', RedemptionViewSet)
router.register(r'admin/rewards', AdminRewardViewSet, basename='admin-reward')  # Use unique basename
router.register(r'user-redemptions', UserRedemptionViewSet, basename='user-redemption')
router.register(r'points-rates', PointsRateViewSet, basename='points-rates')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', AnalyticsDataView.as_view(), name='analytics_data'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
