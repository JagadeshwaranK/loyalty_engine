from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Reward, Campaign, Redemption, PointsRate

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('tier', 'points')}),
    )
    list_display = ('username', 'email', 'tier', 'points', 'is_staff', 'is_active')
    list_filter = ('tier', 'is_staff', 'is_active')

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'active')
    list_editable = ('active',)
    search_fields = ('name',)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_bonus', 'active', 'start_date', 'end_date')
    list_editable = ('points_bonus', 'active')

@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'redeemed_at')
    readonly_fields = ('redeemed_at',)

@admin.register(PointsRate)
class PointsRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'rate', 'active')
    list_editable = ('rate', 'active')
    list_display_links = ('id',)
    list_per_page = 10
