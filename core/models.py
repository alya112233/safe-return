"""
Core models for عودة آمنة - Safe Return
Data models for the reentry support service
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(models.Model):
    """
    Custom user model for the prototype.
    Simulates logged-in users with role-based access.
    In production, this would integrate with Absher / national ID system.
    """
    ROLE_CHOICES = [
        ('beneficiary', 'مستفيد - Beneficiary'),      # Released person
        ('case_worker', 'أخصائي - Case Worker'),      # Social worker
        ('admin', 'مدير - Admin'),                     # System admin
    ]
    
    national_id = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name='رقم الهوية الوطنية'
    )
    full_name = models.CharField(
        max_length=200, 
        verbose_name='الاسم الكامل'
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='beneficiary',
        verbose_name='الدور'
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name='رقم الجوال'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class ReleaseProfile(models.Model):
    """
    Profile for a released person containing their 12-month follow-up plan.
    Linked to a User with role='beneficiary'.
    """
    RISK_LEVEL_CHOICES = [
        ('green', '🟢 أخضر - Green'),    # Low risk, stable
        ('yellow', '🟡 أصفر - Yellow'),  # Medium risk, needs monitoring
        ('red', '🔴 أحمر - Red'),        # High risk, needs intervention
    ]
    
    CITY_CHOICES = [
        ('riyadh', 'الرياض'),
        ('jeddah', 'جدة'),
        ('mecca', 'مكة المكرمة'),
        ('medina', 'المدينة المنورة'),
        ('dammam', 'الدمام'),
        ('khobar', 'الخبر'),
        ('taif', 'الطائف'),
        ('tabuk', 'تبوك'),
        ('other', 'أخرى'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='release_profile',
        verbose_name='المستخدم'
    )
    release_date = models.DateField(
        verbose_name='تاريخ الإفراج'
    )
    end_of_followup_date = models.DateField(
        verbose_name='تاريخ انتهاء المتابعة'
    )
    risk_level = models.CharField(
        max_length=10, 
        choices=RISK_LEVEL_CHOICES, 
        default='green',
        verbose_name='مستوى الخطورة'
    )
    city = models.CharField(
        max_length=50, 
        choices=CITY_CHOICES, 
        default='riyadh',
        verbose_name='المدينة'
    )
    notes = models.TextField(
        blank=True, 
        verbose_name='ملاحظات'
    )
    assigned_case_worker = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_profiles',
        limit_choices_to={'role': 'case_worker'},
        verbose_name='الأخصائي المسؤول'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='مكتمل'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ملف الإفراج'
        verbose_name_plural = 'ملفات الإفراج'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"ملف {self.user.full_name} - {self.get_risk_level_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate end of followup date (12 months from release)
        if self.release_date and not self.end_of_followup_date:
            self.end_of_followup_date = self.release_date + timedelta(days=365)
        super().save(*args, **kwargs)
    
    @property
    def current_month(self):
        """Calculate which month of the 12-month plan we're in."""
        if not self.release_date:
            return 0
        days_since_release = (timezone.now().date() - self.release_date).days
        month = (days_since_release // 30) + 1
        return min(month, 12)  # Cap at 12 months
    
    @property
    def progress_percentage(self):
        """Calculate progress through the 12-month plan."""
        return min(100, int((self.current_month / 12) * 100))


class MonthlyCheckin(models.Model):
    """
    Monthly check-in form submitted by the beneficiary.
    Captures housing, job, mental, and family status.
    """
    HOUSING_STATUS_CHOICES = [
        ('stable', 'مستقر - Stable'),
        ('temporary', 'مؤقت - Temporary'),
        ('with_family', 'مع العائلة - With Family'),
        ('homeless', 'بدون مأوى - Homeless'),
    ]
    
    JOB_STATUS_CHOICES = [
        ('employed', 'موظف - Employed'),
        ('self_employed', 'عمل حر - Self Employed'),
        ('searching', 'يبحث عن عمل - Searching'),
        ('unemployed', 'عاطل - Unemployed'),
        ('training', 'في تدريب - In Training'),
    ]
    
    MENTAL_STATE_CHOICES = [
        ('good', 'جيد - Good'),
        ('moderate', 'متوسط - Moderate'),
        ('stressed', 'متوتر - Stressed'),
        ('bad', 'سيء - Bad'),
    ]
    
    FAMILY_STATUS_CHOICES = [
        ('supportive', 'داعمة - Supportive'),
        ('neutral', 'محايدة - Neutral'),
        ('problematic', 'مشكلات - Problematic'),
        ('no_contact', 'لا تواصل - No Contact'),
    ]
    
    release_profile = models.ForeignKey(
        ReleaseProfile, 
        on_delete=models.CASCADE, 
        related_name='checkins',
        verbose_name='ملف الإفراج'
    )
    month_index = models.PositiveIntegerField(
        verbose_name='رقم الشهر'
    )  # 1-12
    housing_status = models.CharField(
        max_length=20, 
        choices=HOUSING_STATUS_CHOICES,
        verbose_name='حالة السكن'
    )
    job_status = models.CharField(
        max_length=20, 
        choices=JOB_STATUS_CHOICES,
        verbose_name='حالة العمل'
    )
    mental_state = models.CharField(
        max_length=20, 
        choices=MENTAL_STATE_CHOICES,
        verbose_name='الحالة النفسية'
    )
    family_status = models.CharField(
        max_length=20, 
        choices=FAMILY_STATUS_CHOICES,
        verbose_name='حالة العائلة'
    )
    free_text_notes = models.TextField(
        blank=True, 
        verbose_name='ملاحظات إضافية'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'متابعة شهرية'
        verbose_name_plural = 'المتابعات الشهرية'
        ordering = ['-month_index']
        unique_together = ['release_profile', 'month_index']
    
    def __str__(self):
        return f"متابعة الشهر {self.month_index} - {self.release_profile.user.full_name}"


class JobOpportunity(models.Model):
    """
    Job opportunities that can be recommended to beneficiaries.
    """
    CITY_CHOICES = ReleaseProfile.CITY_CHOICES
    
    title = models.CharField(
        max_length=200, 
        verbose_name='المسمى الوظيفي'
    )
    company = models.CharField(
        max_length=200, 
        verbose_name='الشركة',
        blank=True
    )
    description = models.TextField(
        verbose_name='الوصف'
    )
    city = models.CharField(
        max_length=50, 
        choices=CITY_CHOICES,
        verbose_name='المدينة'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    link_url = models.URLField(
        blank=True,
        verbose_name='رابط التقديم'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'فرصة عمل'
        verbose_name_plural = 'فرص العمل'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_city_display()}"


class SupportTicket(models.Model):
    """
    Support tickets for beneficiaries.
    Can be created by the system (auto) or by case workers.
    """
    TYPE_CHOICES = [
        ('job', '💼 دعم وظيفي - Job Support'),
        ('social', '🤝 دعم اجتماعي - Social Support'),
        ('psychological', '🧠 دعم نفسي - Psychological Support'),
        ('housing', '🏠 دعم سكني - Housing Support'),
        ('financial', '💰 دعم مالي - Financial Support'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'مفتوح - Open'),
        ('in_progress', 'قيد المعالجة - In Progress'),
        ('resolved', 'تم الحل - Resolved'),
        ('closed', 'مغلق - Closed'),
    ]
    
    release_profile = models.ForeignKey(
        ReleaseProfile, 
        on_delete=models.CASCADE, 
        related_name='tickets',
        verbose_name='ملف الإفراج'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_tickets',
        verbose_name='أنشئ بواسطة'
    )
    ticket_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES,
        verbose_name='نوع التذكرة'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='open',
        verbose_name='الحالة'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات'
    )
    is_auto_generated = models.BooleanField(
        default=False,
        verbose_name='إنشاء تلقائي'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تذكرة دعم'
        verbose_name_plural = 'تذاكر الدعم'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_ticket_type_display()} - {self.release_profile.user.full_name}"


class Notification(models.Model):
    """
    Notifications for users (both beneficiaries and case workers).
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='المستخدم'
    )
    message = models.TextField(
        verbose_name='الرسالة'
    )
    link = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='الرابط'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='تمت القراءة'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f"{status} {self.message[:50]}..."
