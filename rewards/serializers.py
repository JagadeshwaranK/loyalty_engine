from rest_framework import serializers
from .models import User, Reward, Campaign, Redemption, PointsRate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[])

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password', 'role', 'tier', 'points')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'user'),
            tier=validated_data.get('tier', 'Bronze'),
            points=validated_data.get('points', 0)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class RedemptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    reward = RewardSerializer(read_only=True)
    reward_id = serializers.PrimaryKeyRelatedField(queryset=Reward.objects.all(), write_only=True, source='reward')

    class Meta:
        model = Redemption
        fields = ('id', 'user', 'reward', 'reward_id', 'redeemed_at', 'coupon_code', 'used')

    def create(self, validated_data):
        return Redemption.objects.create(**validated_data)

class PointsRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsRate
        fields = '__all__'
