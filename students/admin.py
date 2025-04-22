from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Student, ParentStudent
from accounts.models import User
from parents.models import Parent

class StudentParentInline(admin.TabularInline):
    model = ParentStudent
    fk_name = 'student'
    extra = 1
    verbose_name = _('Phụ huynh')
    verbose_name_plural = _('Danh sách phụ huynh')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Parent.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'gender', 'current_grade', 'admission_date', 'age', 'get_parents_display')
    list_filter = ('gender', 'admission_date', 'current_grade')
    search_fields = ('student_id', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('age',)
    inlines = [StudentParentInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'student_id', 'gender', 'admission_date')
        }),
        (_('Thông tin học tập'), {
            'fields': ('current_grade', 'previous_school')
        }),
        (_('Thông tin sức khỏe'), {
            'fields': ('blood_group', 'health_status', 'allergies', 'height', 'weight'),
            'classes': ('collapse',),
        }),
        (_('Thông tin khác'), {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Họ và tên')
    
    def get_parents_display(self, obj):
        parents = obj.get_parents
        if parents:
            return ", ".join([p.user.get_full_name() for p in parents])
        return _("Chưa có")
    get_parents_display.short_description = _('Phụ huynh')
    
    def age(self, obj):
        return obj.age
    age.short_description = _('Tuổi')

class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'relationship', 'is_primary')
    list_filter = ('relationship', 'is_primary')
    search_fields = (
        'parent__user__first_name', 'parent__user__last_name', 
        'student__user__first_name', 'student__user__last_name', 'student__student_id'
    )
    
    fieldsets = (
        (None, {
            'fields': ('parent', 'student', 'relationship', 'is_primary')
        }),
        (_('Thông tin bổ sung'), {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )

admin.site.register(Student, StudentAdmin)
admin.site.register(ParentStudent, ParentStudentAdmin)
