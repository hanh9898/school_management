from django.db import models
from django.utils.translation import gettext_lazy as _
from teachers.models import Teacher
from students.models import Student

class AcademicYear(models.Model):
    """Model năm học"""
    name = models.CharField(_('tên năm học'), max_length=50, unique=True)
    start_date = models.DateField(_('ngày bắt đầu'))
    end_date = models.DateField(_('ngày kết thúc'))
    is_current = models.BooleanField(_('là năm học hiện tại'), default=False)
    
    class Meta:
        verbose_name = _('năm học')
        verbose_name_plural = _('năm học')
    
    def __str__(self):
        return self.name

class Grade(models.Model):
    """Model khối lớp (1, 2, 3, 4, 5)"""
    name = models.CharField(_('tên khối'), max_length=50, unique=True)
    description = models.TextField(_('mô tả'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('khối lớp')
        verbose_name_plural = _('khối lớp')
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    """Model môn học"""
    name = models.CharField(_('tên môn học'), max_length=100)
    code = models.CharField(_('mã môn học'), max_length=20, unique=True)
    description = models.TextField(_('mô tả'), blank=True, null=True)
    grades = models.ManyToManyField(Grade, related_name='subjects', verbose_name=_('khối lớp'))
    
    class Meta:
        verbose_name = _('môn học')
        verbose_name_plural = _('môn học')
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class ClassRoom(models.Model):
    """Model lớp học"""
    name = models.CharField(_('tên lớp'), max_length=50)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes', verbose_name=_('khối lớp'))
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='classes', verbose_name=_('năm học'))
    homeroom_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, related_name='homeroom_classes', null=True, blank=True, verbose_name=_('giáo viên chủ nhiệm'))
    students = models.ManyToManyField(Student, through='ClassroomStudent', related_name='classes', verbose_name=_('học sinh'))
    
    # Thông tin bổ sung
    room_number = models.CharField(_('số phòng'), max_length=20, blank=True, null=True)
    max_students = models.PositiveIntegerField(_('số học sinh tối đa'), default=35)
    
    class Meta:
        verbose_name = _('lớp học')
        verbose_name_plural = _('lớp học')
        unique_together = ('name', 'academic_year')
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"
    
    @property
    def student_count(self):
        return self.students.count()

class ClassroomStudent(models.Model):
    """Model liên kết học sinh và lớp học"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('học sinh'))
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, verbose_name=_('lớp học'))
    date_joined = models.DateField(_('ngày vào lớp'), auto_now_add=True)
    
    # Thông tin bổ sung
    roll_number = models.PositiveIntegerField(_('số thứ tự'), null=True, blank=True)
    status = models.CharField(_('trạng thái'), max_length=20, default='active',
                              choices=(
                                  ('active', _('Đang học')),
                                  ('transferred', _('Đã chuyển')),
                                  ('graduated', _('Đã tốt nghiệp')),
                                  ('suspended', _('Tạm nghỉ')),
                              ))
    
    class Meta:
        verbose_name = _('học sinh trong lớp')
        verbose_name_plural = _('học sinh trong lớp')
        unique_together = ('student', 'classroom')
    
    def __str__(self):
        return f"{self.student} - {self.classroom}"

class TeacherSubjectClass(models.Model):
    """Model phân công giảng dạy"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teaching_assignments', verbose_name=_('giáo viên'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teaching_assignments', verbose_name=_('môn học'))
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='teaching_assignments', verbose_name=_('lớp học'))
    
    class Meta:
        verbose_name = _('phân công giảng dạy')
        verbose_name_plural = _('phân công giảng dạy')
        unique_together = ('teacher', 'subject', 'classroom')
    
    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.classroom}"

class Timetable(models.Model):
    """Model thời khóa biểu"""
    DAY_CHOICES = (
        (0, _('Thứ hai')),
        (1, _('Thứ ba')),
        (2, _('Thứ tư')),
        (3, _('Thứ năm')),
        (4, _('Thứ sáu')),
        (5, _('Thứ bảy')),
        (6, _('Chủ nhật')),
    )
    
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='timetable_entries', verbose_name=_('lớp học'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries', verbose_name=_('môn học'))
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetable_entries', verbose_name=_('giáo viên'))
    day_of_week = models.IntegerField(_('ngày trong tuần'), choices=DAY_CHOICES)
    start_time = models.TimeField(_('thời gian bắt đầu'))
    end_time = models.TimeField(_('thời gian kết thúc'))
    
    class Meta:
        verbose_name = _('thời khóa biểu')
        verbose_name_plural = _('thời khóa biểu')
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} | {self.subject} | {self.classroom}"
