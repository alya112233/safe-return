"""
URL routing for عودة آمنة - Safe Return core app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# DRF Router for API endpoints
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ReleaseProfileViewSet)
router.register(r'checkins', views.MonthlyCheckinViewSet)
router.register(r'jobs', views.JobOpportunityViewSet)
router.register(r'tickets', views.SupportTicketViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    # ==========================================================================
    # Template-based views (UI)
    # ==========================================================================
    
    # Login/Logout
    path('', views.absher_login, name='absher_login'),  # Main entry - Absher login for beneficiaries
    path('caseworker/login/', views.login_select, name='login_select'),  # Case workers login
    path('logout/', views.logout_view, name='logout'),
    
    # Beneficiary routes
    path('beneficiary/dashboard/', views.beneficiary_dashboard, name='beneficiary_dashboard'),
    path('beneficiary/checkin/', views.checkin_form, name='checkin_form'),
    path('beneficiary/checkin/<int:month_index>/', views.checkin_form, name='checkin_form_month'),
    path('beneficiary/jobs/', views.job_list, name='job_list'),
    path('beneficiary/messages/', views.beneficiary_messages, name='beneficiary_messages'),
    path('beneficiary/support/', views.support_services, name='support_services'),
    
    # Case worker routes
    path('caseworker/dashboard/', views.caseworker_dashboard, name='caseworker_dashboard'),
    path('caseworker/profile/<int:profile_id>/', views.profile_detail, name='profile_detail'),
    path('caseworker/profile/<int:profile_id>/ticket/', views.create_ticket, name='create_ticket'),
    path('caseworker/profile/<int:profile_id>/complete/', views.mark_profile_completed, name='mark_profile_completed'),
    path('caseworker/ticket/<int:ticket_id>/status/', views.update_ticket_status, name='update_ticket_status'),
    
    # Notifications
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # ==========================================================================
    # REST API routes
    # ==========================================================================
    path('api/', include(router.urls)),
]

