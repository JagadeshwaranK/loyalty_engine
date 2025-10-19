from django.shortcuts import render
from .utils import get_tokens_for_user
# Create your views here.
from rest_framework import viewsets, permissions, status, serializers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Reward, Campaign, Redemption, PointsRate
from .serializers import UserSerializer, RewardSerializer, CampaignSerializer, RedemptionSerializer, RewardSerializer, PointsRateSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsAdminUser, IsRegularUser
import uuid

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Assign role based on is_staff or is_superuser flags
        if user.is_superuser or user.is_staff:
            token['role'] = 'admin'  # Staff and superuser get admin role for frontend routing
        else:
            token['role'] = 'user'

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Assign role based on is_staff or is_superuser flags
        if user.is_superuser or user.is_staff:
            token['role'] = 'admin'  # Staff and superuser get admin role for frontend routing
        else:
            token['role'] = 'user'

        return token

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # For demo, allow all, Update for production

    def get_permissions(self):
        if self.request.method == 'OPTIONS':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def points(self, request):
        user = request.user
        rewards = Reward.objects.filter(active=True)
        serializer = RewardSerializer(rewards, many=True)
        return Response({
            'points': user.points,
            'rewards': serializer.data
        })


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.filter(active=True)
    serializer_class = RewardSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def redeem(self, request, pk=None):
        reward = self.get_object()
        user = request.user

        if user.points < reward.points_required:
            return Response({'error': 'Insufficient points'}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct points and create redemption
        user.points -= reward.points_required
        user.save()

        # Generate unique coupon code
        coupon_code = str(uuid.uuid4())[:8].upper()
        redemption = Redemption.objects.create(user=user, reward=reward, coupon_code=coupon_code)

        return Response({'message': 'Reward redeemed successfully', 'coupon_code': coupon_code})


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.filter(active=True)
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]


class RedemptionViewSet(viewsets.ModelViewSet):
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        reward = serializer.validated_data['reward']

        if user.points < reward.points_required:
            raise serializers.ValidationError('Insufficient points to redeem this reward')

        # Deduct points and save redemption
        user.points -= reward.points_required
        user.save()

        serializer.save(user=user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_used(self, request, pk=None):
        redemption = self.get_object()
        if redemption.user != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        redemption.used = True
        redemption.save()
        return Response({'message': 'Redemption marked as used'})

class AdminRewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class UserRedemptionViewSet(viewsets.ModelViewSet):
    queryset = Redemption.objects.all().order_by('-redeemed_at')
    serializer_class = RedemptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsRegularUser]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class PointsRateViewSet(viewsets.ModelViewSet):
    queryset = PointsRate.objects.filter(active=True)
    serializer_class = PointsRateSerializer
    permission_classes = [permissions.AllowAny]
