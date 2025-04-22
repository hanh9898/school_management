from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from classes.models import ClassRoom, Subject

User = settings.AUTH_USER_MODEL

class DocumentCategory(models.Model):
    """Model danh mục tài liệu"""
    name = models.CharField(_('tên danh mục'), max_length=100)
    description = models.TextField(_('mô tả'), blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('danh mục cha'))
    
    class Meta:
        verbose_name = _('danh mục tài liệu')
        verbose_name_plural = _('danh mục tài liệu')
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

class Document(models.Model):
    """Model tài liệu học tập"""
    TYPE_CHOICES = (
        ('textbook', _('Sách giáo khoa')),
        ('worksheet', _('Bài tập')),
        ('exam', _('Đề kiểm tra')),
        ('lesson', _('Giáo án')),
        ('presentation', _('Bài thuyết trình')),
        ('reference', _('Tài liệu tham khảo')),
        ('other', _('Khác')),
    )
    
    ACCESS_LEVEL_CHOICES = (
        ('public', _('Công khai')),
        ('teachers', _('Chỉ giáo viên')),
        ('class', _('Chỉ lớp cụ thể')),
        ('private', _('Riêng tư')),
    )
    
    title = models.CharField(_('tiêu đề'), max_length=200)
    description = models.TextField(_('mô tả'), blank=True, null=True)
    file = models.FileField(_('tệp tin'), upload_to='documents/')
    thumbnail = models.ImageField(_('hình thu nhỏ'), upload_to='thumbnails/', null=True, blank=True)
    
    # Phân loại
    document_type = models.CharField(_('loại tài liệu'), max_length=20, choices=TYPE_CHOICES)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name=_('danh mục'))
    
    # Liên kết
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name=_('môn học'))
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name=_('lớp học'))
    
    # Quyền truy cập
    access_level = models.CharField(_('mức độ truy cập'), max_length=20, choices=ACCESS_LEVEL_CHOICES, default='public')
    
    # Thông tin thêm
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents', verbose_name=_('người tải lên'))
    created_at = models.DateTimeField(_('thời gian tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('cập nhật lần cuối'), auto_now=True)
    
    # Số liệu thống kê
    views = models.PositiveIntegerField(_('lượt xem'), default=0)
    downloads = models.PositiveIntegerField(_('lượt tải'), default=0)
    
    class Meta:
        verbose_name = _('tài liệu')
        verbose_name_plural = _('tài liệu')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def file_size(self):
        """Trả về kích thước tệp tin dưới dạng đọc được cho con người"""
        if self.file:
            size_bytes = self.file.size
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes/(1024*1024):.1f} MB"
            else:
                return f"{size_bytes/(1024*1024*1024):.1f} GB"
        return "0 B"
    file_size.short_description = _('Kích thước')

class DocumentAccess(models.Model):
    """Model lưu trữ thông tin truy cập tài liệu"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_logs', verbose_name=_('tài liệu'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_access_logs', verbose_name=_('người dùng'))
    accessed_at = models.DateTimeField(_('thời gian truy cập'), auto_now_add=True)
    is_download = models.BooleanField(_('là lượt tải về'), default=False)
    
    class Meta:
        verbose_name = _('lượt truy cập tài liệu')
        verbose_name_plural = _('lượt truy cập tài liệu')
        ordering = ['-accessed_at']
    
    def __str__(self):
        access_type = _('Tải về') if self.is_download else _('Xem')
        return f"{access_type}: {self.user} - {self.document} ({self.accessed_at.strftime('%d/%m/%Y %H:%M')})"
