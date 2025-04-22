from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from parents.models import Parent

class Student(models.Model):
    """Model thông tin học sinh"""
    BLOOD_TYPES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('Unknown', _('Không rõ')),
    )
    
    GENDER_CHOICES = (
        ('male', _('Nam')),
        ('female', _('Nữ')),
        ('other', _('Khác')),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(_('mã học sinh'), max_length=20, unique=True)
    gender = models.CharField(_('giới tính'), max_length=10, choices=GENDER_CHOICES)
    admission_date = models.DateField(_('ngày nhập học'))
    blood_group = models.CharField(_('nhóm máu'), max_length=10, choices=BLOOD_TYPES, default='Unknown')
    current_grade = models.CharField(_('lớp hiện tại'), max_length=20, blank=True, null=True)
    previous_school = models.CharField(_('trường học trước đây'), max_length=255, blank=True, null=True)
    height = models.FloatField(_('chiều cao (cm)'), blank=True, null=True)
    weight = models.FloatField(_('cân nặng (kg)'), blank=True, null=True)
    
    # Thông tin sức khỏe
    health_status = models.TextField(_('tình trạng sức khỏe'), blank=True, null=True)
    allergies = models.TextField(_('dị ứng'), blank=True, null=True)
    
    # Thông tin khác
    notes = models.TextField(_('ghi chú'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('học sinh')
        verbose_name_plural = _('học sinh')
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    @property
    def get_parents(self):
        return Parent.objects.filter(parentstudent__student=self)
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        born = self.user.date_of_birth
        if born:
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None

# Model liên kết giữa phụ huynh và học sinh
class ParentStudent(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='student_relationships')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parent_relationships')
    relationship = models.CharField(_('quan hệ'), max_length=50, choices=[
        ('father', _('Cha')),
        ('mother', _('Mẹ')),
        ('guardian', _('Người giám hộ')),
        ('other', _('Khác')),
    ])
    is_primary = models.BooleanField(_('là người giám hộ chính'), default=False)
    notes = models.TextField(_('ghi chú'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('quan hệ phụ huynh-học sinh')
        verbose_name_plural = _('quan hệ phụ huynh-học sinh')
        unique_together = ('parent', 'student')
        
    def __str__(self):
        return f"{self.parent.user.get_full_name()} - {self.get_relationship_display()} của {self.student.user.get_full_name()}"
