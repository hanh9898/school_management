from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from classes.models import Subject, ClassRoom
from students.models import Student
from teachers.models import Teacher

class ExamType(models.Model):
    """Model loại kiểm tra"""
    name = models.CharField(_('tên loại kiểm tra'), max_length=100)
    description = models.TextField(_('mô tả'), blank=True, null=True)
    weight = models.FloatField(_('trọng số'), default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    
    class Meta:
        verbose_name = _('loại kiểm tra')
        verbose_name_plural = _('loại kiểm tra')
    
    def __str__(self):
        return self.name

class Exam(models.Model):
    """Model bài kiểm tra"""
    title = models.CharField(_('tiêu đề'), max_length=200)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='exams', verbose_name=_('loại kiểm tra'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams', verbose_name=_('môn học'))
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='exams', verbose_name=_('lớp học'))
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='exams', verbose_name=_('giáo viên'))
    exam_date = models.DateField(_('ngày kiểm tra'))
    max_score = models.FloatField(_('điểm tối đa'), default=10.0)
    description = models.TextField(_('mô tả'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('bài kiểm tra')
        verbose_name_plural = _('bài kiểm tra')
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"{self.title} - {self.subject} - {self.classroom}"

class Grade(models.Model):
    """Model điểm số"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades', verbose_name=_('học sinh'))
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades', verbose_name=_('bài kiểm tra'))
    score = models.FloatField(_('điểm số'), validators=[MinValueValidator(0.0)])
    comments = models.TextField(_('nhận xét'), blank=True, null=True)
    date_graded = models.DateTimeField(_('ngày chấm điểm'), auto_now_add=True)
    last_updated = models.DateTimeField(_('cập nhật lần cuối'), auto_now=True)
    
    class Meta:
        verbose_name = _('điểm số')
        verbose_name_plural = _('điểm số')
        unique_together = ('student', 'exam')
    
    def __str__(self):
        return f"{self.student} - {self.exam}: {self.score}"

class AcademicReport(models.Model):
    """Model báo cáo học tập"""
    TERM_CHOICES = (
        ('1', _('Học kỳ 1')),
        ('2', _('Học kỳ 2')),
        ('final', _('Cả năm')),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_reports', verbose_name=_('học sinh'))
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='academic_reports', verbose_name=_('lớp học'))
    term = models.CharField(_('học kỳ'), max_length=10, choices=TERM_CHOICES)
    average_score = models.FloatField(_('điểm trung bình'), validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    rank = models.CharField(_('xếp loại'), max_length=20, blank=True, null=True)
    teacher_comments = models.TextField(_('nhận xét của giáo viên'), blank=True, null=True)
    parent_comments = models.TextField(_('nhận xét của phụ huynh'), blank=True, null=True)
    date_created = models.DateField(_('ngày tạo'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('báo cáo học tập')
        verbose_name_plural = _('báo cáo học tập')
        unique_together = ('student', 'classroom', 'term')
    
    def __str__(self):
        return f"{self.student} - {self.classroom} - {self.get_term_display()}"

class SubjectReport(models.Model):
    """Model báo cáo môn học"""
    academic_report = models.ForeignKey(AcademicReport, on_delete=models.CASCADE, related_name='subject_reports', verbose_name=_('báo cáo học tập'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_reports', verbose_name=_('môn học'))
    average_score = models.FloatField(_('điểm trung bình'), validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    comments = models.TextField(_('nhận xét'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('báo cáo môn học')
        verbose_name_plural = _('báo cáo môn học')
        unique_together = ('academic_report', 'subject')
    
    def __str__(self):
        return f"{self.academic_report.student} - {self.subject}: {self.average_score}"
