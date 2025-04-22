from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Announcement, Message, Notification, Feedback

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'audience', 'classroom', 'is_important', 'publish_date', 'expiry_date', 'created_at')
    list_filter = ('audience', 'is_important', 'publish_date', 'created_by')
    search_fields = ('title', 'content', 'created_by__first_name', 'created_by__last_name')
    date_hierarchy = 'publish_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'created_by')
        }),
        (_('Đối tượng nhận'), {
            'fields': ('audience', 'classroom')
        }),
        (_('Thời gian'), {
            'fields': ('publish_date', 'expiry_date', 'is_important')
        }),
        (_('Tệp đính kèm'), {
            'fields': ('attachment',)
        }),
    )

class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'receiver', 'created_at', 'is_read', 'read_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('subject', 'content', 'sender__first_name', 'sender__last_name', 'receiver__first_name', 'receiver__last_name')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'subject', 'content')
        }),
        (_('Trạng thái'), {
            'fields': ('is_read', 'read_at')
        }),
        (_('Tệp đính kèm'), {
            'fields': ('attachment',)
        }),
    )
    
    readonly_fields = ('created_at', 'read_at')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'created_at', 'is_read', 'read_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'content', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'content', 'notification_type')
        }),
        (_('Liên kết'), {
            'fields': ('content_type', 'object_id')
        }),
        (_('Trạng thái'), {
            'fields': ('is_read', 'read_at')
        }),
    )
    
    readonly_fields = ('created_at', 'read_at')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'assigned_to', 'created_at', 'responded_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'content', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'content', 'category')
        }),
        (_('Trạng thái và xử lý'), {
            'fields': ('status', 'assigned_to', 'response', 'responded_at')
        }),
        (_('Tệp đính kèm'), {
            'fields': ('attachment',)
        }),
    )
    
    readonly_fields = ('created_at', 'responded_at')

admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Feedback, FeedbackAdmin)
