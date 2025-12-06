"""
DRF Serializers for عودة آمنة - Safe Return
REST API serialization for all models.
"""

from rest_framework import serializers
from .models import (
    User, ReleaseProfile, MonthlyCheckin, 
    JobOpportunity, SupportTicket, Notification
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'national_id', 'full_name', 'role', 'role_display', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']


class MonthlyCheckinSerializer(serializers.ModelSerializer):
    """Serializer for MonthlyCheckin model."""
    housing_status_display = serializers.CharField(source='get_housing_status_display', read_only=True)
    job_status_display = serializers.CharField(source='get_job_status_display', read_only=True)
    mental_state_display = serializers.CharField(source='get_mental_state_display', read_only=True)
    family_status_display = serializers.CharField(source='get_family_status_display', read_only=True)
    
    class Meta:
        model = MonthlyCheckin
        fields = [
            'id', 'release_profile', 'month_index',
            'housing_status', 'housing_status_display',
            'job_status', 'job_status_display',
            'mental_state', 'mental_state_display',
            'family_status', 'family_status_display',
            'free_text_notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    """Serializer for SupportTicket model."""
    ticket_type_display = serializers.CharField(source='get_ticket_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'release_profile', 'created_by', 'created_by_name',
            'ticket_type', 'ticket_type_display',
            'status', 'status_display',
            'notes', 'is_auto_generated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReleaseProfileSerializer(serializers.ModelSerializer):
    """Serializer for ReleaseProfile model."""
    user = UserSerializer(read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    current_month = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    assigned_case_worker_name = serializers.CharField(
        source='assigned_case_worker.full_name', 
        read_only=True
    )
    checkins = MonthlyCheckinSerializer(many=True, read_only=True)
    tickets = SupportTicketSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReleaseProfile
        fields = [
            'id', 'user', 'release_date', 'end_of_followup_date',
            'risk_level', 'risk_level_display',
            'city', 'city_display',
            'notes', 'assigned_case_worker', 'assigned_case_worker_name',
            'is_completed', 'current_month', 'progress_percentage',
            'checkins', 'tickets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReleaseProfileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing profiles."""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_national_id = serializers.CharField(source='user.national_id', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    current_month = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    open_tickets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReleaseProfile
        fields = [
            'id', 'user_name', 'user_national_id',
            'risk_level', 'risk_level_display',
            'city', 'city_display',
            'current_month', 'progress_percentage',
            'open_tickets_count', 'is_completed'
        ]
    
    def get_open_tickets_count(self, obj):
        return obj.tickets.filter(status='open').count()


class JobOpportunitySerializer(serializers.ModelSerializer):
    """Serializer for JobOpportunity model."""
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    
    class Meta:
        model = JobOpportunity
        fields = [
            'id', 'title', 'company', 'description',
            'city', 'city_display', 'is_active', 'link_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'link', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

