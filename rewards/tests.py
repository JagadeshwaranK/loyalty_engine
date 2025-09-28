from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, Reward, Redemption

class RewardTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='adminpass', is_staff=True)
        self.admin_user.role = 'admin'
        self.admin_user.save()
        self.regular_user = User.objects.create_user(username='user', password='userpass')
        self.client = APIClient()

    def test_admin_can_create_reward(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('rewards:admin-reward-list')
        data = {
            'name': 'Test Reward',
            'points_required': 100,
            'redemption_type': 'amount_discount',
            'amount_discount': 10.0,
            'active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reward.objects.count(), 1)
        self.assertEqual(Reward.objects.get().name, 'Test Reward')

    def test_regular_user_cannot_create_reward(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('rewards:admin-reward-list')
        data = {
            'name': 'Test Reward',
            'points_required': 100,
            'redemption_type': 'amount_discount',
            'amount_discount': 10.0,
            'active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_redeem_reward_and_points_deducted(self):
        reward = Reward.objects.create(
            name='Redeemable Reward',
            points_required=50,
            redemption_type='amount_discount',
            amount_discount=5.0,
            active=True
        )
        self.regular_user.points = 100
        self.regular_user.save()
        self.client.force_authenticate(user=self.regular_user)
        url = '/api/redemptions/'
        data = {'reward_id': reward.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.points, 50)  # 100 - 50 points_required

    def test_user_cannot_redeem_reward_without_enough_points(self):
        reward = Reward.objects.create(
            name='Expensive Reward',
            points_required=200,
            redemption_type='amount_discount',
            amount_discount=20.0,
            active=True
        )
        self.regular_user.points = 100
        self.regular_user.save()
        self.client.force_authenticate(user=self.regular_user)
        url = '/api/redemptions/'
        data = {'reward_id': reward.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
