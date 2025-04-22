from django.db import models
from django.utils.translation import gettext_lazy as _
from classes.models import ClassRoom
from students.models import Student
from teachers.models import Teacher

class AttendanceRecord(models.Model):
    """Model ghi nhận điểm danh của lớp học trong một ngày"""
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='attendance_records', verbose_name=_('lớp học'))
    date = models.DateField(_('ngày'))
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_records', verbose_name=_('giáo viên điểm danh'))
    notes = models.TextField(_('ghi chú'), blank=True, null=True)
    created_at = models.DateTimeField(_('thời gian tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('cập nhật lần cuối'), auto_now=True)
    
    class Meta:
        verbose_name = _('bản ghi điểm danh')
        verbose_name_plural = _('bản ghi điểm danh')
        unique_together = ('classroom', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.classroom} - {self.date}"

class Attendance(models.Model):
    """Model điểm danh của từng học sinh"""
    STATUS_CHOICES = (
        ('present', _('Có mặt')),
        ('absent', _('Vắng mặt')),
        ('excused', _('Có phép')),
        ('late', _('Đi muộn')),
        ('sick', _('Ốm')),
    )
    
    attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name='attendances', verbose_name=_('bản ghi điểm danh'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name=_('học sinh'))
    status = models.CharField(_('trạng thái'), max_length=20, choices=STATUS_CHOICES, default='present')
    reason = models.TextField(_('lý do'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('điểm danh')
        verbose_name_plural = _('điểm danh')
        unique_together = ('attendance_record', 'student')
    
    def __str__(self):
        return f"{self.student} - {self.attendance_record.date} - {self.get_status_display()}"

class LeaveRequest(models.Model):
    """Model yêu cầu nghỉ phép"""
    STATUS_CHOICES = (
        ('pending', _('Đang chờ duyệt')),
        ('approved', _('Đã duyệt')),
        ('rejected', _('Từ chối')),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_requests', verbose_name=_('học sinh'))
    start_date = models.DateField(_('ngày bắt đầu'))
    end_date = models.DateField(_('ngày kết thúc'))
    reason = models.TextField(_('lý do'))
    
    # Thông tin phê duyệt
    status = models.CharField(_('trạng thái'), max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves', verbose_name=_('người duyệt'))
    reviewer_comment = models.TextField(_('nhận xét của người duyệt'), blank=True, null=True)
    
    # Thông tin thêm
    parent_contact = models.CharField(_('liên hệ phụ huynh'), max_length=100, blank=True, null=True)
    medical_certificate = models.FileField(_('giấy chứng nhận y tế'), upload_to='leave_certificates/', blank=True, null=True)
    
    # Thông tin thời gian
    created_at = models.DateTimeField(_('thời gian tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('cập nhật lần cuối'), auto_now=True)
    
    class Meta:
        verbose_name = _('yêu cầu nghỉ phép')
        verbose_name_plural = _('yêu cầu nghỉ phép')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.start_date} đến {self.end_date} - {self.get_status_display()}"
