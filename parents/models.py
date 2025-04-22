from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Parent(models.Model):
    """Model thông tin phụ huynh"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    occupation = models.CharField(_('nghề nghiệp'), max_length=100, blank=True, null=True)
    workplace = models.CharField(_('nơi làm việc'), max_length=255, blank=True, null=True)
    education = models.CharField(_('trình độ học vấn'), max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(_('người liên hệ khẩn cấp'), max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(_('số điện thoại khẩn cấp'), max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = _('phụ huynh')
        verbose_name_plural = _('phụ huynh')
    
    def __str__(self):
        return f"{self.user.get_full_name()}"
    
    @property
    def get_children(self):
        from students.models import Student
        return Student.objects.filter(parent_relationships__parent=self)
