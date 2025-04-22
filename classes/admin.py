from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    AcademicYear, Grade, Subject, ClassRoom, 
    ClassroomStudent, TeacherSubjectClass, Timetable
)

class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)

class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    filter_horizontal = ('grades',)

class ClassroomStudentInline(admin.TabularInline):
    model = ClassroomStudent
    extra = 1

class TeacherSubjectClassInline(admin.TabularInline):
    model = TeacherSubjectClass
    extra = 1

class TimetableInline(admin.TabularInline):
    model = Timetable
    extra = 1
    ordering = ('day_of_week', 'start_time')

class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'academic_year', 'homeroom_teacher', 'room_number', 'student_count')
    list_filter = ('grade', 'academic_year')
    search_fields = ('name', 'homeroom_teacher__user__first_name', 'homeroom_teacher__user__last_name')
    inlines = [ClassroomStudentInline, TeacherSubjectClassInline, TimetableInline]
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = _('Số lượng học sinh')

class ClassroomStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'roll_number', 'status', 'date_joined')
    list_filter = ('classroom', 'status')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'classroom__name')

class TeacherSubjectClassAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'classroom')
    list_filter = ('subject', 'classroom')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'subject__name', 'classroom__name')

class TimetableAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time', 'subject', 'teacher', 'classroom')
    list_filter = ('day_of_week', 'classroom', 'subject')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'subject__name', 'classroom__name')
    ordering = ('day_of_week', 'start_time')

admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(ClassRoom, ClassRoomAdmin)
admin.site.register(ClassroomStudent, ClassroomStudentAdmin)
admin.site.register(TeacherSubjectClass, TeacherSubjectClassAdmin)
admin.site.register(Timetable, TimetableAdmin)
