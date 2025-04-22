from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import DocumentCategory, Document, DocumentAccess

class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name', 'description')
    list_filter = ('parent',)

class DocumentAccessInline(admin.TabularInline):
    model = DocumentAccess
    extra = 0
    readonly_fields = ('user', 'accessed_at', 'is_download')
    max_num = 10
    
    def has_add_permission(self, request, obj=None):
        return False

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'subject', 'classroom', 'category', 'uploaded_by', 'access_level', 'created_at', 'display_file_size', 'views', 'downloads')
    list_filter = ('document_type', 'access_level', 'subject', 'classroom', 'category')
    search_fields = ('title', 'description', 'uploaded_by__first_name', 'uploaded_by__last_name')
    date_hierarchy = 'created_at'
    inlines = [DocumentAccessInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'file', 'thumbnail')
        }),
        (_('Phân loại'), {
            'fields': ('document_type', 'category')
        }),
        (_('Liên kết'), {
            'fields': ('subject', 'classroom')
        }),
        (_('Quyền truy cập'), {
            'fields': ('access_level', 'uploaded_by')
        }),
        (_('Số liệu thống kê'), {
            'fields': ('views', 'downloads')
        }),
    )
    
    def display_file_size(self, obj):
        return obj.file_size()
    display_file_size.short_description = _('Kích thước')

class DocumentAccessAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'accessed_at', 'is_download')
    list_filter = ('is_download', 'accessed_at', 'document__document_type')
    search_fields = ('document__title', 'user__first_name', 'user__last_name')
    date_hierarchy = 'accessed_at'
    readonly_fields = ('document', 'user', 'accessed_at', 'is_download')
    
    def has_add_permission(self, request):
        return False

admin.site.register(DocumentCategory, DocumentCategoryAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentAccess, DocumentAccessAdmin)
