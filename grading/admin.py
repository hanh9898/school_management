from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ExamType, Exam, Grade, AcademicReport, SubjectReport

class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1

class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'description')
    search_fields = ('name',)

class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type', 'subject', 'classroom', 'teacher', 'exam_date', 'max_score')
    list_filter = ('exam_type', 'subject', 'classroom', 'exam_date')
    search_fields = ('title', 'teacher__user__first_name', 'teacher__user__last_name')
    date_hierarchy = 'exam_date'
    inlines = [GradeInline]

class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'date_graded', 'last_updated')
    list_filter = ('exam__subject', 'exam__classroom', 'exam__exam_type')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'exam__title')
    date_hierarchy = 'date_graded'

class SubjectReportInline(admin.TabularInline):
    model = SubjectReport
    extra = 1

class AcademicReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'term', 'average_score', 'rank', 'date_created')
    list_filter = ('term', 'classroom', 'rank')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'classroom__name')
    date_hierarchy = 'date_created'
    inlines = [SubjectReportInline]

class SubjectReportAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'subject', 'average_score', 'get_term')
    list_filter = ('subject', 'academic_report__term')
    search_fields = ('academic_report__student__user__first_name', 'academic_report__student__user__last_name', 'subject__name')
    
    def get_student(self, obj):
        return obj.academic_report.student
    get_student.short_description = _('Học sinh')
    
    def get_term(self, obj):
        return obj.academic_report.get_term_display()
    get_term.short_description = _('Học kỳ')

admin.site.register(ExamType, ExamTypeAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(AcademicReport, AcademicReportAdmin)
admin.site.register(SubjectReport, SubjectReportAdmin)
