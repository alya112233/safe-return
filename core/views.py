"""
Views for عودة آمنة - Safe Return
Both template-based views and DRF API views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import (
    User, ReleaseProfile, MonthlyCheckin, 
    JobOpportunity, SupportTicket, Notification
)
from .serializers import (
    UserSerializer, ReleaseProfileSerializer, ReleaseProfileListSerializer,
    MonthlyCheckinSerializer, JobOpportunitySerializer, 
    SupportTicketSerializer, NotificationSerializer
)
from .risk_engine import process_checkin, get_risk_summary


# =============================================================================
# Template-Based Views (for hackathon UI)
# =============================================================================

@csrf_exempt
def absher_login(request):
    """
    Absher-style login for beneficiaries using national ID.
    This simulates the real Absher experience.
    """
    error = None
    
    if request.method == 'POST':
        national_id = request.POST.get('national_id', '').strip()
        
        try:
            user = User.objects.get(national_id=national_id, role='beneficiary')
            request.session['user_id'] = user.id
            return redirect('beneficiary_dashboard')
        except User.DoesNotExist:
            error = 'رقم الهوية غير مسجل في برنامج عودة آمنة'
    
    return render(request, 'core/absher_login.html', {'error': error})


@csrf_exempt
def login_select(request):
    """
    Login selector for case workers and support organizations.
    Beneficiaries should use absher_login instead.
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            request.session['user_id'] = int(user_id)
            user = User.objects.get(id=user_id)
            if user.role == 'beneficiary':
                return redirect('beneficiary_dashboard')
            else:
                return redirect('caseworker_dashboard')
    
    # Only show case workers and admins, not beneficiaries
    users = User.objects.filter(role__in=['case_worker', 'admin']).order_by('role', 'full_name')
    return render(request, 'core/login_select.html', {'users': users})


def logout_view(request):
    """Clear session and return to login."""
    request.session.flush()
    return redirect('login_select')


def get_current_user(request):
    """Helper to get current simulated user from session."""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    return None


# -----------------------------------------------------------------------------
# Beneficiary Views
# -----------------------------------------------------------------------------

def beneficiary_dashboard(request):
    """
    Main dashboard for beneficiaries (released persons).
    Shows their 12-month plan progress, notifications, and tickets.
    """
    user = get_current_user(request)
    if not user or user.role != 'beneficiary':
        return redirect('login_select')
    
    try:
        profile = user.release_profile
    except ReleaseProfile.DoesNotExist:
        return render(request, 'core/no_profile.html', {'user': user})
    
    # Get checkins organized by month
    checkins = {c.month_index: c for c in profile.checkins.all()}
    months = []
    for i in range(1, 13):
        months.append({
            'number': i,
            'checkin': checkins.get(i),
            'is_current': i == profile.current_month,
            'is_past': i < profile.current_month,
            'is_future': i > profile.current_month,
        })
    
    # Get notifications
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    
    # Get open tickets
    open_tickets = profile.tickets.filter(status__in=['open', 'in_progress'])
    
    # Get job recommendations (same city)
    jobs = JobOpportunity.objects.filter(is_active=True, city=profile.city)[:3]
    
    context = {
        'user': user,
        'profile': profile,
        'months': months,
        'notifications': notifications,
        'open_tickets': open_tickets,
        'jobs': jobs,
        'risk_summary': get_risk_summary(profile),
    }
    return render(request, 'core/beneficiary_dashboard.html', context)


def checkin_form(request, month_index=None):
    """
    Monthly check-in form for beneficiaries.
    """
    user = get_current_user(request)
    if not user or user.role != 'beneficiary':
        return redirect('login_select')
    
    try:
        profile = user.release_profile
    except ReleaseProfile.DoesNotExist:
        return redirect('beneficiary_dashboard')
    
    # Use current month if not specified
    if month_index is None:
        month_index = profile.current_month
    
    # Check if already submitted
    existing_checkin = profile.checkins.filter(month_index=month_index).first()
    
    if request.method == 'POST':
        # Create or update check-in
        checkin, created = MonthlyCheckin.objects.update_or_create(
            release_profile=profile,
            month_index=month_index,
            defaults={
                'housing_status': request.POST.get('housing_status'),
                'job_status': request.POST.get('job_status'),
                'mental_state': request.POST.get('mental_state'),
                'family_status': request.POST.get('family_status'),
                'free_text_notes': request.POST.get('free_text_notes', ''),
            }
        )
        
        # Process the check-in (calculate risk, create tickets)
        result = process_checkin(checkin)
        
        messages.success(request, f'✅ تم حفظ المتابعة الشهرية للشهر {month_index}')
        return redirect('beneficiary_dashboard')
    
    context = {
        'user': user,
        'profile': profile,
        'month_index': month_index,
        'existing_checkin': existing_checkin,
        'housing_choices': MonthlyCheckin.HOUSING_STATUS_CHOICES,
        'job_choices': MonthlyCheckin.JOB_STATUS_CHOICES,
        'mental_choices': MonthlyCheckin.MENTAL_STATE_CHOICES,
        'family_choices': MonthlyCheckin.FAMILY_STATUS_CHOICES,
    }
    return render(request, 'core/checkin_form.html', context)


def beneficiary_messages(request):
    """
    Messaging page for beneficiary to communicate with case worker.
    """
    user = get_current_user(request)
    if not user or user.role != 'beneficiary':
        return redirect('login_select')
    
    try:
        profile = user.release_profile
    except ReleaseProfile.DoesNotExist:
        return redirect('beneficiary_dashboard')
    
    if request.method == 'POST':
        message_type = request.POST.get('message_type')
        message_content = request.POST.get('message_content')
        
        # Create a notification for the case worker
        if profile.assigned_case_worker:
            Notification.objects.create(
                user=profile.assigned_case_worker,
                message=f'📩 رسالة جديدة من {user.full_name}: {message_content[:50]}...',
                link=f'/caseworker/profile/{profile.id}/'
            )
        
        messages.success(request, '✅ تم إرسال رسالتك بنجاح! سيتواصل معك الأخصائي قريباً.')
        return redirect('beneficiary_messages')
    
    context = {
        'user': user,
        'profile': profile,
        'messages_list': [],  # Would be real messages in production
    }
    return render(request, 'core/beneficiary_messages.html', context)


def support_services(request):
    """
    List of support services and organizations for beneficiaries.
    """
    user = get_current_user(request)
    if not user or user.role != 'beneficiary':
        return redirect('login_select')
    
    context = {
        'user': user,
    }
    return render(request, 'core/support_services.html', context)


def job_list(request):
    """
    List of available job opportunities for beneficiaries.
    """
    user = get_current_user(request)
    if not user or user.role != 'beneficiary':
        return redirect('login_select')
    
    try:
        profile = user.release_profile
        user_city = profile.city
    except ReleaseProfile.DoesNotExist:
        user_city = None
    
    # Get jobs, prioritizing user's city
    if user_city:
        jobs_in_city = JobOpportunity.objects.filter(is_active=True, city=user_city)
        jobs_other = JobOpportunity.objects.filter(is_active=True).exclude(city=user_city)
        jobs = list(jobs_in_city) + list(jobs_other)
    else:
        jobs = JobOpportunity.objects.filter(is_active=True)
    
    context = {
        'user': user,
        'jobs': jobs,
        'user_city': user_city,
    }
    return render(request, 'core/job_list.html', context)


# -----------------------------------------------------------------------------
# Case Worker Views
# -----------------------------------------------------------------------------

def caseworker_dashboard(request):
    """
    Dashboard for case workers showing all profiles and risk levels.
    """
    user = get_current_user(request)
    if not user or user.role not in ['case_worker', 'admin']:
        return redirect('login_select')
    
    # Get filter parameters
    risk_filter = request.GET.get('risk', '')
    city_filter = request.GET.get('city', '')
    
    # Get all profiles (or assigned to this caseworker)
    profiles = ReleaseProfile.objects.select_related('user').prefetch_related('checkins', 'tickets')
    
    if risk_filter:
        profiles = profiles.filter(risk_level=risk_filter)
    if city_filter:
        profiles = profiles.filter(city=city_filter)
    
    # Count by risk level for summary
    risk_counts = {
        'red': ReleaseProfile.objects.filter(risk_level='red', is_completed=False).count(),
        'yellow': ReleaseProfile.objects.filter(risk_level='yellow', is_completed=False).count(),
        'green': ReleaseProfile.objects.filter(risk_level='green', is_completed=False).count(),
    }
    
    # Get notifications for this caseworker
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    
    context = {
        'user': user,
        'profiles': profiles.filter(is_completed=False),
        'risk_counts': risk_counts,
        'notifications': notifications,
        'risk_filter': risk_filter,
        'city_filter': city_filter,
        'cities': ReleaseProfile.CITY_CHOICES,
    }
    return render(request, 'core/caseworker_dashboard.html', context)


def profile_detail(request, profile_id):
    """
    Detailed view of a beneficiary's profile for case workers.
    """
    user = get_current_user(request)
    if not user or user.role not in ['case_worker', 'admin']:
        return redirect('login_select')
    
    profile = get_object_or_404(ReleaseProfile, id=profile_id)
    
    # Get all checkins
    checkins = profile.checkins.all().order_by('month_index')
    
    # Get all tickets
    tickets = profile.tickets.all()
    
    # Get risk summary
    risk_summary = get_risk_summary(profile)
    
    context = {
        'user': user,
        'profile': profile,
        'checkins': checkins,
        'tickets': tickets,
        'risk_summary': risk_summary,
        'ticket_types': SupportTicket.TYPE_CHOICES,
    }
    return render(request, 'core/profile_detail.html', context)


def create_ticket(request, profile_id):
    """
    Create a new support ticket for a beneficiary.
    """
    user = get_current_user(request)
    if not user or user.role not in ['case_worker', 'admin']:
        return redirect('login_select')
    
    profile = get_object_or_404(ReleaseProfile, id=profile_id)
    
    if request.method == 'POST':
        ticket = SupportTicket.objects.create(
            release_profile=profile,
            created_by=user,
            ticket_type=request.POST.get('ticket_type'),
            notes=request.POST.get('notes', ''),
            is_auto_generated=False,
        )
        
        # Notify the beneficiary
        Notification.objects.create(
            user=profile.user,
            message=f'📋 تم فتح تذكرة دعم جديدة: {ticket.get_ticket_type_display()}',
            link='/beneficiary/dashboard/'
        )
        
        messages.success(request, '✅ تم إنشاء التذكرة بنجاح')
        return redirect('profile_detail', profile_id=profile_id)
    
    context = {
        'user': user,
        'profile': profile,
        'ticket_types': SupportTicket.TYPE_CHOICES,
    }
    return render(request, 'core/create_ticket.html', context)


@require_POST
def update_ticket_status(request, ticket_id):
    """
    Update a ticket's status (AJAX endpoint).
    """
    user = get_current_user(request)
    if not user or user.role not in ['case_worker', 'admin']:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(SupportTicket.STATUS_CHOICES):
        ticket.status = new_status
        ticket.save()
        
        # Notify beneficiary of status change
        Notification.objects.create(
            user=ticket.release_profile.user,
            message=f'📋 تم تحديث حالة التذكرة: {ticket.get_status_display()}',
            link='/beneficiary/dashboard/'
        )
        
        return JsonResponse({'success': True, 'new_status': ticket.get_status_display()})
    
    return JsonResponse({'error': 'Invalid status'}, status=400)


@require_POST
def mark_profile_completed(request, profile_id):
    """
    Mark a profile's 12-month followup as completed.
    """
    user = get_current_user(request)
    if not user or user.role not in ['case_worker', 'admin']:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    profile = get_object_or_404(ReleaseProfile, id=profile_id)
    profile.is_completed = True
    profile.save()
    
    # Notify beneficiary
    Notification.objects.create(
        user=profile.user,
        message='🎉 تهانينا! تم إكمال برنامج المتابعة الخاص بك بنجاح',
        link='/beneficiary/dashboard/'
    )
    
    messages.success(request, '✅ تم إكمال المتابعة بنجاح')
    return redirect('caseworker_dashboard')


@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    notification = get_object_or_404(Notification, id=notification_id, user=user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})


# =============================================================================
# REST API ViewSets (for API access)
# =============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ReleaseProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for release profiles."""
    queryset = ReleaseProfile.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReleaseProfileListSerializer
        return ReleaseProfileSerializer
    
    @action(detail=True, methods=['get'])
    def risk_summary(self, request, pk=None):
        """Get risk summary for a profile."""
        profile = self.get_object()
        summary = get_risk_summary(profile)
        # Convert checkin to serialized form
        if summary.get('latest_checkin'):
            summary['latest_checkin'] = MonthlyCheckinSerializer(summary['latest_checkin']).data
        return Response(summary)


class MonthlyCheckinViewSet(viewsets.ModelViewSet):
    """API endpoint for monthly check-ins."""
    queryset = MonthlyCheckin.objects.all()
    serializer_class = MonthlyCheckinSerializer
    
    def perform_create(self, serializer):
        """Process checkin after creation."""
        checkin = serializer.save()
        process_checkin(checkin)


class JobOpportunityViewSet(viewsets.ModelViewSet):
    """API endpoint for job opportunities."""
    queryset = JobOpportunity.objects.filter(is_active=True)
    serializer_class = JobOpportunitySerializer


class SupportTicketViewSet(viewsets.ModelViewSet):
    """API endpoint for support tickets."""
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for notifications."""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'read'})
