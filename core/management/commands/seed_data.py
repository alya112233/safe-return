"""
Seed data command for عودة آمنة - Safe Return
Creates demo data for hackathon presentation.

Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from core.models import (
    User, ReleaseProfile, MonthlyCheckin,
    JobOpportunity, SupportTicket, Notification
)


class Command(BaseCommand):
    help = 'Seeds the database with demo data for Safe Return hackathon'

    def handle(self, *args, **options):
        self.stdout.write('🌱 بدء إنشاء البيانات التجريبية...\n')
        
        # Clear existing data
        self.stdout.write('🗑️  حذف البيانات السابقة...')
        Notification.objects.all().delete()
        SupportTicket.objects.all().delete()
        MonthlyCheckin.objects.all().delete()
        ReleaseProfile.objects.all().delete()
        JobOpportunity.objects.all().delete()
        User.objects.all().delete()
        
        # Create Case Workers
        self.stdout.write('👨‍💼 إنشاء حسابات الأخصائيين...')
        caseworker1 = User.objects.create(
            national_id='1234567890',
            full_name='فهد الزهراني',
            role='case_worker',
            phone='0551234567'
        )
        caseworker2 = User.objects.create(
            national_id='1234567891',
            full_name='سارة القحطاني',
            role='case_worker',
            phone='0559876543'
        )
        
        # Create Beneficiaries with different scenarios
        self.stdout.write('👤 إنشاء حسابات المستفيدين...')
        
        # Beneficiary 1: Good progress (Green)
        user1 = User.objects.create(
            national_id='1111111111',
            full_name='أحمد محمد العتيبي',
            role='beneficiary',
            phone='0501112222'
        )
        profile1 = ReleaseProfile.objects.create(
            user=user1,
            release_date=timezone.now().date() - timedelta(days=90),  # 3 months ago
            city='riyadh',
            risk_level='green',
            assigned_case_worker=caseworker1,
            notes='حالة مستقرة، عاد للعمل في ورشة والده'
        )
        # Add check-ins for months 1-3
        for month in range(1, 4):
            MonthlyCheckin.objects.create(
                release_profile=profile1,
                month_index=month,
                housing_status='with_family',
                job_status='self_employed',
                mental_state='good',
                family_status='supportive',
                free_text_notes='الحمد لله، الأمور تسير بشكل جيد'
            )
        
        # Beneficiary 2: Medium risk (Yellow) - needs job support
        user2 = User.objects.create(
            national_id='2222222222',
            full_name='خالد سعد الغامدي',
            role='beneficiary',
            phone='0502223333'
        )
        profile2 = ReleaseProfile.objects.create(
            user=user2,
            release_date=timezone.now().date() - timedelta(days=60),  # 2 months ago
            city='jeddah',
            risk_level='yellow',
            assigned_case_worker=caseworker1,
            notes='يحتاج دعم في إيجاد عمل مناسب'
        )
        MonthlyCheckin.objects.create(
            release_profile=profile2,
            month_index=1,
            housing_status='with_family',
            job_status='searching',
            mental_state='moderate',
            family_status='supportive'
        )
        MonthlyCheckin.objects.create(
            release_profile=profile2,
            month_index=2,
            housing_status='with_family',
            job_status='unemployed',
            mental_state='stressed',
            family_status='supportive',
            free_text_notes='أبحث عن عمل لكن لم أجد حتى الآن'
        )
        SupportTicket.objects.create(
            release_profile=profile2,
            ticket_type='job',
            status='in_progress',
            notes='تم التنسيق مع طاقات لترشيحه لوظيفة أمن',
            is_auto_generated=True
        )
        
        # Beneficiary 3: High risk (Red) - needs urgent intervention
        user3 = User.objects.create(
            national_id='3333333333',
            full_name='عبدالله فيصل الدوسري',
            role='beneficiary',
            phone='0503334444'
        )
        profile3 = ReleaseProfile.objects.create(
            user=user3,
            release_date=timezone.now().date() - timedelta(days=30),  # 1 month ago
            city='dammam',
            risk_level='red',
            assigned_case_worker=caseworker2,
            notes='حالة تحتاج متابعة مكثفة - مشكلات أسرية'
        )
        MonthlyCheckin.objects.create(
            release_profile=profile3,
            month_index=1,
            housing_status='temporary',
            job_status='unemployed',
            mental_state='bad',
            family_status='problematic',
            free_text_notes='العائلة رافضة استقبالي، أحتاج مساعدة عاجلة'
        )
        SupportTicket.objects.create(
            release_profile=profile3,
            ticket_type='psychological',
            status='open',
            notes='حالة نفسية سيئة - يحتاج جلسة عاجلة',
            is_auto_generated=True
        )
        SupportTicket.objects.create(
            release_profile=profile3,
            ticket_type='housing',
            status='open',
            notes='بحاجة لسكن مؤقت',
            is_auto_generated=True
        )
        SupportTicket.objects.create(
            release_profile=profile3,
            ticket_type='social',
            status='open',
            notes='محاولة إصلاح العلاقة الأسرية',
            created_by=caseworker2,
            is_auto_generated=False
        )
        
        # Beneficiary 4: New case (just released)
        user4 = User.objects.create(
            national_id='4444444444',
            full_name='محمد علي الشهري',
            role='beneficiary',
            phone='0504445555'
        )
        profile4 = ReleaseProfile.objects.create(
            user=user4,
            release_date=timezone.now().date() - timedelta(days=5),  # 5 days ago
            city='riyadh',
            risk_level='green',
            assigned_case_worker=caseworker1,
            notes='حالة جديدة - تم الإفراج مؤخراً'
        )
        
        # Beneficiary 5: Almost completed (month 11)
        user5 = User.objects.create(
            national_id='5555555555',
            full_name='سلطان ناصر المطيري',
            role='beneficiary',
            phone='0505556666'
        )
        profile5 = ReleaseProfile.objects.create(
            user=user5,
            release_date=timezone.now().date() - timedelta(days=330),  # 11 months ago
            city='mecca',
            risk_level='green',
            assigned_case_worker=caseworker2,
            notes='حالة نموذجية - قارب على إكمال البرنامج'
        )
        # Add all 11 check-ins
        for month in range(1, 12):
            MonthlyCheckin.objects.create(
                release_profile=profile5,
                month_index=month,
                housing_status='stable',
                job_status='employed',
                mental_state='good',
                family_status='supportive'
            )
        
        # Create Job Opportunities
        self.stdout.write('💼 إنشاء فرص العمل...')
        jobs_data = [
            {
                'title': 'حارس أمن',
                'company': 'شركة الحماية الأمنية',
                'description': 'مطلوب حارس أمن للعمل في مجمع تجاري. الراتب 4000-5000 ريال. دوام كامل.',
                'city': 'riyadh',
                'link_url': 'https://example.com/job1'
            },
            {
                'title': 'سائق توصيل',
                'company': 'شركة توصيل سريع',
                'description': 'مطلوب سائق توصيل طلبات. يشترط رخصة قيادة سارية. راتب + عمولة.',
                'city': 'riyadh',
                'link_url': 'https://example.com/job2'
            },
            {
                'title': 'عامل في مصنع',
                'company': 'مصنع الخليج للبلاستيك',
                'description': 'فرصة عمل في خط الإنتاج. تدريب مجاني. راتب 3500 ريال + تأمين.',
                'city': 'dammam',
                'link_url': 'https://example.com/job3'
            },
            {
                'title': 'مساعد طباخ',
                'company': 'مطعم الديوان',
                'description': 'مطلوب مساعد طباخ. لا يشترط خبرة. راتب 3000 ريال + وجبات.',
                'city': 'jeddah',
                'link_url': ''
            },
            {
                'title': 'فني صيانة',
                'company': 'ورشة الأمل',
                'description': 'مطلوب فني صيانة سيارات. خبرة سنة على الأقل. راتب حسب الخبرة.',
                'city': 'riyadh',
                'link_url': 'https://example.com/job5'
            },
            {
                'title': 'عامل نظافة',
                'company': 'شركة نظافة الخليج',
                'description': 'فرص عمل متعددة في مجال النظافة. دوامات مرنة. راتب 3000 ريال.',
                'city': 'mecca',
                'link_url': ''
            },
            {
                'title': 'بائع في معرض',
                'company': 'معرض الفرسان للسيارات',
                'description': 'مطلوب بائع للعمل في معرض سيارات. راتب + عمولة مجزية.',
                'city': 'jeddah',
                'link_url': 'https://example.com/job7'
            },
        ]
        
        for job_data in jobs_data:
            JobOpportunity.objects.create(**job_data)
        
        # Create some notifications
        self.stdout.write('🔔 إنشاء الإشعارات...')
        Notification.objects.create(
            user=caseworker1,
            message='⚠️ تنبيه: عبدالله الدوسري يحتاج دعم نفسي عاجل',
            link='/caseworker/profile/3/'
        )
        Notification.objects.create(
            user=caseworker2,
            message='📋 تذكير: متابعة حالة سلطان المطيري - الشهر الأخير',
            link='/caseworker/profile/5/'
        )
        Notification.objects.create(
            user=user2,
            message='💼 تم ترشيحك لوظيفة جديدة! تحقق من التفاصيل',
            link='/beneficiary/jobs/'
        )
        Notification.objects.create(
            user=user4,
            message='👋 مرحباً بك في برنامج عودة آمنة! يرجى تعبئة المتابعة الأولى',
            link='/beneficiary/checkin/1/'
        )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ تم إنشاء البيانات التجريبية بنجاح!'))
        self.stdout.write('='*50)
        self.stdout.write(f'\n📊 ملخص البيانات:')
        self.stdout.write(f'   • الأخصائيون: {User.objects.filter(role="case_worker").count()}')
        self.stdout.write(f'   • المستفيدون: {User.objects.filter(role="beneficiary").count()}')
        self.stdout.write(f'   • ملفات الإفراج: {ReleaseProfile.objects.count()}')
        self.stdout.write(f'   • المتابعات الشهرية: {MonthlyCheckin.objects.count()}')
        self.stdout.write(f'   • فرص العمل: {JobOpportunity.objects.count()}')
        self.stdout.write(f'   • تذاكر الدعم: {SupportTicket.objects.count()}')
        self.stdout.write(f'   • الإشعارات: {Notification.objects.count()}')
        
        self.stdout.write(f'\n🚀 يمكنك الآن تشغيل الخادم:')
        self.stdout.write(f'   python manage.py runserver')
        self.stdout.write(f'\n🌐 ثم افتح: http://127.0.0.1:8000/')

