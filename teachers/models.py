from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Teacher(models.Model):
    """Model thông tin giáo viên"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField(_('mã giáo viên'), max_length=20, unique=True)
    
    QUALIFICATION_CHOICES = (
        ('bachelor', _('Cử nhân')),
        ('master', _('Thạc sĩ')),
        ('phd', _('Tiến sĩ')),
        ('other', _('Khác')),
    )
    
    date_of_joining = models.DateField(_('ngày vào làm'))
    qualification = models.CharField(_('bằng cấp'), max_length=20, choices=QUALIFICATION_CHOICES, default='bachelor')
    experience = models.PositiveIntegerField(_('kinh nghiệm (năm)'), default=0)
    specialization = models.CharField(_('chuyên môn'), max_length=100)
    
    # Thông tin liên hệ khẩn cấp
    emergency_contact_name = models.CharField(_('tên người liên hệ khẩn cấp'), max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(_('số điện thoại khẩn cấp'), max_length=15, blank=True, null=True)
    
    # Thông tin khác
    notes = models.TextField(_('ghi chú'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('giáo viên')
        verbose_name_plural = _('giáo viên')
    
    def __str__(self):
        return f"{self.teacher_id} - {self.user.get_full_name()}"
