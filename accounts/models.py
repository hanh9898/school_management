from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
import datetime

from .permissions import sync_user_permissions


class UserManager(BaseUserManager):
    """Quản lý việc tạo người dùng tùy chỉnh"""

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_("Username là bắt buộc"))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser phải có is_superuser=True."))

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    """Model người dùng tùy chỉnh với các role"""

    ROLE_CHOICES = (
        ("admin", _("Quản trị viên")),
        ("teacher", _("Giáo viên")),
        ("parent", _("Phụ huynh")),
        ("student", _("Học sinh")),
    )

    # username từ AbstractUser đã được giữ lại
    email = models.EmailField(_("địa chỉ email"), unique=True, blank=True, null=True)
    role = models.CharField(
        _("vai trò"), max_length=10, choices=ROLE_CHOICES, default="student"
    )

    # Thêm validation cho số điện thoại (định dạng Việt Nam)
    phone_regex = RegexValidator(
        regex=r"^(0|\+84)(\s|\.)?((3[2-9])|(5[2689])|(7[06-9])|(8[1-689])|(9[0-9]))(\d)(\s|\.)?(\d{3})(\s|\.)?(\d{3})$",
        message=_(
            "Số điện thoại phải đúng định dạng Việt Nam. Ví dụ: +84 912 345 678 hoặc 0912345678"
        ),
    )
    phone_number = models.CharField(
        _("số điện thoại"),
        validators=[phone_regex],
        max_length=15,
        blank=True,
        null=True,
    )

    address = models.TextField(_("địa chỉ"), blank=True, null=True)

    # Thêm validation cho ngày sinh
    def validate_birth_date(value):
        today = timezone.now().date()
        min_date = today - datetime.timedelta(days=365 * 100)  # Không quá 100 tuổi
        max_date = today  # Không được sinh sau ngày hiện tại

        if value and (value < min_date or value > max_date):
            raise models.ValidationError(_("Ngày sinh không hợp lệ"))

    date_of_birth = models.DateField(
        _("ngày sinh"), validators=[validate_birth_date], blank=True, null=True
    )

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Tùy chỉnh các quyền
    custom_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("quyền hạn tùy chỉnh"),
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
        help_text=_("Quyền hạn cụ thể cho người dùng này ngoài các quyền mặc định."),
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("người dùng")
        verbose_name_plural = _("người dùng")
        permissions = [
            ("view_student_info", _("Xem thông tin học sinh")),
            ("edit_student_info", _("Chỉnh sửa thông tin học sinh")),
            ("view_grades", _("Xem điểm số")),
            ("edit_grades", _("Chỉnh sửa điểm số")),
            ("view_attendance", _("Xem điểm danh")),
            ("edit_attendance", _("Chỉnh sửa điểm danh")),
            ("view_timetable", _("Xem thời khóa biểu")),
            ("edit_timetable", _("Chỉnh sửa thời khóa biểu")),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def get_full_name(self):
        """Trả về họ và tên đầy đủ của người dùng."""
        full_name = f"{self.last_name} {self.first_name}"
        return full_name.strip()

    def save(self, *args, **kwargs):
        # Kiểm tra nếu đây là tạo mới hoặc role đã thay đổi
        is_new = self.pk is None

        # Nếu không phải tạo mới, lấy role cũ để kiểm tra thay đổi
        if not is_new:
            try:
                old_instance = User.objects.get(pk=self.pk)
                old_role = old_instance.role
            except User.DoesNotExist:
                old_role = None
        else:
            old_role = None

        # Lưu instance
        super().save(*args, **kwargs)

        # Đồng bộ quyền nếu là tạo mới hoặc role đã thay đổi
        if is_new or old_role != self.role:
            self._assign_default_permissions()

    def _assign_default_permissions(self):
        # Sử dụng module permissions để đồng bộ quyền
        sync_user_permissions(self)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_teacher(self):
        return self.role == "teacher"

    @property
    def is_parent(self):
        return self.role == "parent"

    @property
    def is_student(self):
        return self.role == "student"
