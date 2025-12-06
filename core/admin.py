"""
Django Admin configuration for عودة آمنة - Safe Return.
"""

from django.contrib import admin
from .models import (
    User, ReleaseProfile, MonthlyCheckin,
    JobOpportunity, SupportTicket, Notification
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'national_id', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['full_name', 'national_id', 'phone']


@admin.register(ReleaseProfile)
class ReleaseProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'risk_level', 'city', 'release_date', 'is_completed']
    list_filter = ['risk_level', 'city', 'is_completed']
    search_fields = ['user__full_name', 'user__national_id']
    raw_id_fields = ['user', 'assigned_case_worker']


@admin.register(MonthlyCheckin)
class MonthlyCheckinAdmin(admin.ModelAdmin):
    list_display = ['release_profile', 'month_index', 'housing_status', 'job_status', 'mental_state', 'created_at']
    list_filter = ['month_index', 'housing_status', 'job_status', 'mental_state']
    search_fields = ['release_profile__user__full_name']


@admin.register(JobOpportunity)
class JobOpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'city', 'is_active', 'created_at']
    list_filter = ['city', 'is_active']
    search_fields = ['title', 'company', 'description']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['release_profile', 'ticket_type', 'status', 'is_auto_generated', 'created_at']
    list_filter = ['ticket_type', 'status', 'is_auto_generated']
    search_fields = ['release_profile__user__full_name', 'notes']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__full_name', 'message']
