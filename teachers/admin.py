from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Teacher

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'get_full_name', 'specialization', 'qualification', 'experience', 'date_of_joining')
    list_filter = ('qualification', 'date_of_joining')
    search_fields = ('teacher_id', 'user__first_name', 'user__last_name', 'specialization')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Họ và tên')

admin.site.register(Teacher, TeacherAdmin)
