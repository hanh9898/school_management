from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from classes.models import ClassRoom

User = settings.AUTH_USER_MODEL

class Announcement(models.Model):
    """Model thông báo chung của nhà trường"""
    AUDIENCE_CHOICES = (
        ('all', _('Toàn trường')),
        ('teachers', _('Giáo viên')),
        ('parents', _('Phụ huynh')),
        ('students', _('Học sinh')),
        ('class', _('Lớp cụ thể')),
    )
    
    title = models.CharField(_('tiêu đề'), max_length=200)
    content = models.TextField(_('nội dung'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements', verbose_name=_('người tạo'))
    created_at = models.DateTimeField(_('thời gian tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('cập nhật lần cuối'), auto_now=True)
    
    audience = models.CharField(_('đối tượng'), max_length=20, choices=AUDIENCE_CHOICES, default='all')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='announcements', verbose_name=_('lớp'), null=True, blank=True)
    
    is_important = models.BooleanField(_('quan trọng'), default=False)
    publish_date = models.DateTimeField(_('ngày xuất bản'))
    expiry_date = models.DateTimeField(_('ngày hết hạn'), null=True, blank=True)
    
    # Tệp đính kèm
    attachment = models.FileField(_('tệp đính kèm'), upload_to='announcements/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('thông báo')
        verbose_name_plural = _('thông báo')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Message(models.Model):
    """Model tin nhắn giữa giáo viên và phụ huynh"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name=_('người gửi'))
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name=_('người nhận'))
    subject = models.CharField(_('chủ đề'), max_length=200)
    content = models.TextField(_('nội dung'))
    
    created_at = models.DateTimeField(_('thời gian gửi'), auto_now_add=True)
    read_at = models.DateTimeField(_('thời gian đọc'), null=True, blank=True)
    is_read = models.BooleanField(_('đã đọc'), default=False)
    
    # Tệp đính kèm
    attachment = models.FileField(_('tệp đính kèm'), upload_to='messages/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('tin nhắn')
        verbose_name_plural = _('tin nhắn')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.subject}"

class Notification(models.Model):
    """Model thông báo cho người dùng"""
    TYPE_CHOICES = (
        ('announcement', _('Thông báo chung')),
        ('message', _('Tin nhắn mới')),
        ('grade', _('Điểm mới')),
        ('attendance', _('Điểm danh')),
        ('event', _('Sự kiện')),
        ('leave', _('Yêu cầu nghỉ phép')),
        ('other', _('Khác')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('người dùng'))
    title = models.CharField(_('tiêu đề'), max_length=200)
    content = models.TextField(_('nội dung'))
    notification_type = models.CharField(_('loại thông báo'), max_length=20, choices=TYPE_CHOICES)
    
    # Liên kết đến đối tượng gốc (có thể là thông báo, tin nhắn, sự kiện...)
    content_type = models.CharField(_('loại nội dung'), max_length=100, null=True, blank=True)
    object_id = models.PositiveIntegerField(_('ID đối tượng'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('thời gian tạo'), auto_now_add=True)
    is_read = models.BooleanField(_('đã đọc'), default=False)
    read_at = models.DateTimeField(_('thời gian đọc'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('thông báo')
        verbose_name_plural = _('thông báo')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user}: {self.title}"

class Feedback(models.Model):
    """Model phản hồi từ phụ huynh"""
    STATUS_CHOICES = (
        ('pending', _('Đang chờ xử lý')),
        ('processing', _('Đang xử lý')),
        ('resolved', _('Đã giải quyết')),
        ('closed', _('Đã đóng')),
    )
    
    CATEGORY_CHOICES = (
        ('academic', _('Học tập')),
        ('behavior', _('Hạnh kiểm')),
        ('facility', _('Cơ sở vật chất')),
        ('teacher', _('Giáo viên')),
        ('suggestion', _('Đề xuất')),
        ('other', _('Khác')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', verbose_name=_('người gửi'))
    title = models.CharField(_('tiêu đề'), max_length=200)
    content = models.TextField(_('nội dung'))
    category = models.CharField(_('danh mục'), max_length=20, choices=CATEGORY_CHOICES)
    
    created_at = models.DateTimeField(_('thời gian tạo'), auto_now_add=True)
    status = models.CharField(_('trạng thái'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Thông tin xử lý
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_feedbacks', verbose_name=_('người được giao'))
    response = models.TextField(_('phản hồi'), null=True, blank=True)
    responded_at = models.DateTimeField(_('thời gian phản hồi'), null=True, blank=True)
    
    # Tệp đính kèm
    attachment = models.FileField(_('tệp đính kèm'), upload_to='feedbacks/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('phản hồi')
        verbose_name_plural = _('phản hồi')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user}"
