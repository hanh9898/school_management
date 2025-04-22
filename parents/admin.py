from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Parent
from students.models import ParentStudent
from accounts.models import User

class ParentStudentInline(admin.TabularInline):
    model = ParentStudent
    fk_name = 'parent'
    extra = 1
    verbose_name = _('Học sinh')
    verbose_name_plural = _('Danh sách học sinh')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from students.models import Student
        if db_field.name == "student":
            kwargs["queryset"] = Student.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_formset(self, request, obj=None, **kwargs):
        # Liên kết user với phụ huynh
        if obj:
            self.parent_instance = obj
        return super().get_formset(request, obj, **kwargs)

class ParentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'occupation', 'workplace', 'education', 'get_children_display')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'occupation', 'workplace')
    inlines = [ParentStudentInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'occupation', 'workplace', 'education')
        }),
        (_('Thông tin liên lạc khẩn cấp'), {
            'fields': ('emergency_contact', 'emergency_phone'),
            'classes': ('collapse',),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Họ và tên')
    
    def get_children_display(self, obj):
        children = obj.get_children
        if children:
            return ", ".join([f"{s.student_id} - {s.user.get_full_name()}" for s in children])
        return _("Chưa có")
    get_children_display.short_description = _('Học sinh')

admin.site.register(Parent, ParentAdmin)
