"""
Risk Engine for عودة آمنة - Safe Return
Simple rule-based risk level calculation.

Risk Levels:
- 🔴 RED: High risk, needs immediate intervention
- 🟡 YELLOW: Medium risk, needs monitoring
- 🟢 GREEN: Low risk, stable situation
"""

from .models import ReleaseProfile, SupportTicket, Notification


def calculate_risk_level(checkin):
    """
    Calculate risk level based on monthly check-in data.
    
    Rules:
    - RED if: mental_state == 'bad' OR housing_status == 'homeless'
    - YELLOW if: job_status == 'unemployed' OR family_status == 'problematic'
    - GREEN otherwise
    
    Args:
        checkin: MonthlyCheckin instance
    
    Returns:
        str: 'red', 'yellow', or 'green'
    """
    # Red flags - high risk situations
    red_conditions = [
        checkin.mental_state == 'bad',
        checkin.housing_status == 'homeless',
    ]
    
    # Yellow flags - medium risk situations
    yellow_conditions = [
        checkin.job_status == 'unemployed',
        checkin.family_status == 'problematic',
        checkin.mental_state == 'stressed',
        checkin.family_status == 'no_contact',
    ]
    
    # Determine risk level
    if any(red_conditions):
        return 'red'
    elif any(yellow_conditions):
        return 'yellow'
    else:
        return 'green'


def process_checkin(checkin):
    """
    Process a check-in: calculate risk, update profile, create tickets if needed.
    
    This is called after a beneficiary submits their monthly check-in.
    
    Args:
        checkin: MonthlyCheckin instance
    
    Returns:
        dict: Processing results with risk level and any created tickets
    """
    profile = checkin.release_profile
    
    # Calculate new risk level
    new_risk_level = calculate_risk_level(checkin)
    old_risk_level = profile.risk_level
    
    # Update profile risk level
    profile.risk_level = new_risk_level
    profile.save()
    
    created_tickets = []
    
    # Auto-create support tickets based on check-in data
    
    # Psychological support if mental state is bad
    if checkin.mental_state == 'bad':
        ticket, created = SupportTicket.objects.get_or_create(
            release_profile=profile,
            ticket_type='psychological',
            status='open',
            is_auto_generated=True,
            defaults={
                'notes': f'إنشاء تلقائي: الحالة النفسية سيئة في الشهر {checkin.month_index}'
            }
        )
        if created:
            created_tickets.append(ticket)
            # Notify case worker
            if profile.assigned_case_worker:
                Notification.objects.create(
                    user=profile.assigned_case_worker,
                    message=f'⚠️ تنبيه: {profile.user.full_name} يحتاج دعم نفسي عاجل',
                    link=f'/caseworker/profile/{profile.id}/'
                )
    
    # Housing support if homeless
    if checkin.housing_status == 'homeless':
        ticket, created = SupportTicket.objects.get_or_create(
            release_profile=profile,
            ticket_type='housing',
            status='open',
            is_auto_generated=True,
            defaults={
                'notes': f'إنشاء تلقائي: بدون مأوى في الشهر {checkin.month_index}'
            }
        )
        if created:
            created_tickets.append(ticket)
            # Notify case worker
            if profile.assigned_case_worker:
                Notification.objects.create(
                    user=profile.assigned_case_worker,
                    message=f'🏠 تنبيه: {profile.user.full_name} بدون مأوى',
                    link=f'/caseworker/profile/{profile.id}/'
                )
    
    # Job support if unemployed
    if checkin.job_status == 'unemployed':
        ticket, created = SupportTicket.objects.get_or_create(
            release_profile=profile,
            ticket_type='job',
            status='open',
            is_auto_generated=True,
            defaults={
                'notes': f'إنشاء تلقائي: عاطل عن العمل في الشهر {checkin.month_index}'
            }
        )
        if created:
            created_tickets.append(ticket)
    
    # Social support if family problems
    if checkin.family_status in ['problematic', 'no_contact']:
        ticket, created = SupportTicket.objects.get_or_create(
            release_profile=profile,
            ticket_type='social',
            status='open',
            is_auto_generated=True,
            defaults={
                'notes': f'إنشاء تلقائي: مشكلات عائلية في الشهر {checkin.month_index}'
            }
        )
        if created:
            created_tickets.append(ticket)
    
    # Create notification for beneficiary
    if new_risk_level != old_risk_level:
        risk_messages = {
            'green': '✅ حالتك مستقرة. استمر على هذا النهج!',
            'yellow': '⚠️ هناك بعض المخاوف. سيتواصل معك أخصائي قريباً.',
            'red': '🚨 نحتاج للتواصل معك بشكل عاجل. يرجى الانتظار لمكالمة من الأخصائي.',
        }
        Notification.objects.create(
            user=profile.user,
            message=risk_messages[new_risk_level],
            link='/beneficiary/dashboard/'
        )
    
    return {
        'old_risk_level': old_risk_level,
        'new_risk_level': new_risk_level,
        'risk_changed': old_risk_level != new_risk_level,
        'created_tickets': created_tickets,
    }


def get_risk_summary(profile):
    """
    Get a summary of risk factors for a profile.
    
    Args:
        profile: ReleaseProfile instance
    
    Returns:
        dict: Summary with risk factors and recommendations
    """
    latest_checkin = profile.checkins.first()
    
    if not latest_checkin:
        return {
            'risk_level': 'green',
            'factors': [],
            'recommendations': ['يرجى إكمال أول متابعة شهرية']
        }
    
    factors = []
    recommendations = []
    
    # Analyze latest check-in
    if latest_checkin.mental_state == 'bad':
        factors.append('الحالة النفسية سيئة')
        recommendations.append('إحالة للدعم النفسي عبر خط تراحم')
    
    if latest_checkin.housing_status == 'homeless':
        factors.append('بدون مأوى')
        recommendations.append('التنسيق مع جمعية الإسكان الخيري')
    
    if latest_checkin.job_status == 'unemployed':
        factors.append('عاطل عن العمل')
        recommendations.append('عرض فرص العمل المتاحة في المنطقة')
    
    if latest_checkin.family_status == 'problematic':
        factors.append('مشكلات عائلية')
        recommendations.append('جلسة إرشاد أسري')
    
    if latest_checkin.family_status == 'no_contact':
        factors.append('انقطاع التواصل الأسري')
        recommendations.append('محاولة إعادة بناء الروابط الأسرية')
    
    return {
        'risk_level': profile.risk_level,
        'factors': factors,
        'recommendations': recommendations,
        'latest_checkin': latest_checkin,
    }

