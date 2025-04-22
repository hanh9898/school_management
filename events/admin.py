from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import EventCategory, Event, EventParticipant

class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 1
    readonly_fields = ('registration_date',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'location', 'status', 'created_by', 'created_at', 'registration_required', 'parent_approval_required')
    list_filter = ('status', 'category', 'start_date', 'registration_required', 'parent_approval_required')
    search_fields = ('title', 'description', 'location', 'created_by__first_name', 'created_by__last_name')
    date_hierarchy = 'start_date'
    inlines = [EventParticipantInline]
    filter_horizontal = ('organizers', 'classrooms')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category', 'status')
        }),
        (_('Thời gian và địa điểm'), {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time', 'location')
        }),
        (_('Người tổ chức'), {
            'fields': ('created_by', 'organizers', 'classrooms')
        }),
        (_('Đăng ký'), {
            'fields': ('registration_required', 'registration_deadline', 'max_participants', 'parent_approval_required')
        }),
        (_('Truyền thông'), {
            'fields': ('image', 'attachments')
        }),
    )

class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'registration_date', 'parent_approval', 'approved_by', 'approved_at', 'attended')
    list_filter = ('status', 'parent_approval', 'attended', 'registration_date')
    search_fields = ('user__first_name', 'user__last_name', 'event__title', 'comments')
    date_hierarchy = 'registration_date'
    
    fieldsets = (
        (None, {
            'fields': ('event', 'user', 'status')
        }),
        (_('Phê duyệt'), {
            'fields': ('parent_approval', 'approved_by', 'approved_at')
        }),
        (_('Tham gia'), {
            'fields': ('attended', 'comments')
        }),
    )
    
    readonly_fields = ('registration_date',)

admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventParticipant, EventParticipantAdmin)
