from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AttendanceRecord, Attendance, LeaveRequest

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1
    max_num = 50

class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'date', 'teacher', 'created_at', 'updated_at')
    list_filter = ('classroom', 'date', 'teacher')
    search_fields = ('classroom__name', 'teacher__user__first_name', 'teacher__user__last_name')
    date_hierarchy = 'date'
    inlines = [AttendanceInline]

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_date', 'status', 'reason')
    list_filter = ('status', 'attendance_record__date', 'attendance_record__classroom')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'reason')
    
    def get_date(self, obj):
        return obj.attendance_record.date
    get_date.short_description = _('Ngày')
    get_date.admin_order_field = 'attendance_record__date'

class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'start_date', 'end_date', 'reason', 'status', 'approved_by', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'reason')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('student', 'start_date', 'end_date', 'reason')
        }),
        (_('Thông tin phê duyệt'), {
            'fields': ('status', 'approved_by', 'reviewer_comment')
        }),
        (_('Thông tin bổ sung'), {
            'fields': ('parent_contact', 'medical_certificate')
        }),
        (_('Thời gian'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

admin.site.register(AttendanceRecord, AttendanceRecordAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)
