from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from classes.models import ClassRoom

User = settings.AUTH_USER_MODEL

class EventCategory(models.Model):
    """Model danh mục sự kiện"""
    name = models.CharField(_('tên danh mục'), max_length=100)
    description = models.TextField(_('mô tả'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('danh mục sự kiện')
        verbose_name_plural = _('danh mục sự kiện')
    
    def __str__(self):
        return self.name

class Event(models.Model):
    """Model sự kiện"""
    STATUS_CHOICES = (
        ('draft', _('Nháp')),
        ('published', _('Đã xuất bản')),
        ('cancelled', _('Đã hủy')),
        ('completed', _('Đã hoàn thành')),
    )
    
    title = models.CharField(_('tiêu đề'), max_length=200)
    description = models.TextField(_('mô tả'))
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='events', verbose_name=_('danh mục'))
    
    # Thời gian và địa điểm
    start_date = models.DateField(_('ngày bắt đầu'))
    end_date = models.DateField(_('ngày kết thúc'))
    start_time = models.TimeField(_('giờ bắt đầu'), null=True, blank=True)
    end_time = models.TimeField(_('giờ kết thúc'), null=True, blank=True)
    location = models.CharField(_('địa điểm'), max_length=200)
    
    # Thông tin bổ sung
    status = models.CharField(_('trạng thái'), max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', verbose_name=_('người tạo'))
    organizers = models.ManyToManyField(User, related_name='organized_events', verbose_name=_('người tổ chức'), blank=True)
    classrooms = models.ManyToManyField(ClassRoom, related_name='events', verbose_name=_('lớp tham gia'), blank=True)
    
    max_participants = models.PositiveIntegerField(_('số người tham gia tối đa'), null=True, blank=True)
    registration_required = models.BooleanField(_('yêu cầu đăng ký'), default=False)
    registration_deadline = models.DateTimeField(_('hạn đăng ký'), null=True, blank=True)
    parent_approval_required = models.BooleanField(_('yêu cầu phụ huynh phê duyệt'), default=False)
    
    # Truyền thông
    image = models.ImageField(_('hình ảnh'), upload_to='events/', null=True, blank=True)
    attachments = models.FileField(_('tệp đính kèm'), upload_to='event_attachments/', null=True, blank=True)
    
    # Thời gian quản lý
    created_at = models.DateTimeField(_('thời gian tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('cập nhật lần cuối'), auto_now=True)
    
    class Meta:
        verbose_name = _('sự kiện')
        verbose_name_plural = _('sự kiện')
        ordering = ['-start_date', 'start_time']
    
    def __str__(self):
        return self.title
    
    @property
    def is_upcoming(self):
        """Kiểm tra sự kiện sắp diễn ra hay không"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date >= today and self.status != 'cancelled'
    
    @property
    def is_ongoing(self):
        """Kiểm tra sự kiện đang diễn ra hay không"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'published'
    
    @property
    def participant_count(self):
        """Số lượng người tham gia đã đăng ký"""
        return self.participants.filter(status='approved').count()

class EventParticipant(models.Model):
    """Model người tham gia sự kiện"""
    STATUS_CHOICES = (
        ('pending', _('Đang chờ duyệt')),
        ('approved', _('Đã duyệt')),
        ('rejected', _('Từ chối')),
        ('cancelled', _('Đã hủy')),
        ('attended', _('Đã tham gia')),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants', verbose_name=_('sự kiện'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations', verbose_name=_('người tham gia'))
    
    registration_date = models.DateTimeField(_('ngày đăng ký'), auto_now_add=True)
    status = models.CharField(_('trạng thái'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Thông tin phê duyệt
    parent_approval = models.BooleanField(_('phụ huynh đã duyệt'), default=False, null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_participants', verbose_name=_('người duyệt'))
    approved_at = models.DateTimeField(_('thời gian duyệt'), null=True, blank=True)
    
    # Thông tin tham gia
    attended = models.BooleanField(_('đã tham gia'), default=False)
    comments = models.TextField(_('ghi chú'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('người tham gia sự kiện')
        verbose_name_plural = _('người tham gia sự kiện')
        unique_together = ('event', 'user')
    
    def __str__(self):
        return f"{self.user} - {self.event}"
