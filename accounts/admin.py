from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, Group
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms
import csv
import pandas as pd

from .models import User
from .utils import generate_username_from_name, get_default_password


# Form để import người dùng từ Excel
class ImportExcelForm(forms.Form):
    excel_file = forms.FileField(label=_("File Excel"))


class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "phone_number",
        "is_active",
    )
    list_filter = ("role", "is_active", "groups", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Thông tin cá nhân"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "date_of_birth",
                    "phone_number",
                    "address",
                    "avatar",
                )
            },
        ),
        (
            _("Quyền hạn"),
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "custom_permissions",
                )
            },
        ),
        (_("Ngày quan trọng"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "date_of_birth",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions", "custom_permissions")

    # Thêm hành động hàng loạt
    actions = [
        "activate_accounts",
        "deactivate_accounts",
        "reset_password",
        "export_users_csv",
    ]

    def activate_accounts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"Đã kích hoạt {updated} tài khoản."))

    activate_accounts.short_description = _("Kích hoạt tài khoản đã chọn")

    def deactivate_accounts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"Đã vô hiệu hóa {updated} tài khoản."))

    deactivate_accounts.short_description = _("Vô hiệu hóa tài khoản đã chọn")

    def reset_password(self, request, queryset):
        count = 0
        for user in queryset:
            # Đặt mật khẩu mặc định sử dụng hàm tiện ích
            user.set_password(get_default_password(user))
            user.save(update_fields=["password"])
            count += 1

        self.message_user(
            request,
            _(
                f"Đã đặt lại mật khẩu cho {count} tài khoản. Mật khẩu mặc định là ngày sinh (dd/mm/yyyy) hoặc username nếu không có ngày sinh."
            ),
        )

    reset_password.short_description = _("Đặt lại mật khẩu tài khoản đã chọn")

    def export_users_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "username",
                "email",
                "first_name",
                "last_name",
                "role",
                "phone_number",
                "address",
                "is_active",
            ]
        )

        for user in queryset:
            writer.writerow(
                [
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.role,
                    user.phone_number,
                    user.address,
                    user.is_active,
                ]
            )

        return response

    export_users_csv.short_description = _("Xuất người dùng đã chọn ra CSV")

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel),
                name="accounts_user_import_excel",
            ),
        ]
        return custom_urls + urls

    def _generate_username(self, first_name, last_name):
        return generate_username_from_name(first_name, last_name)

    def import_excel(self, request):
        if request.method == "POST":
            form = ImportExcelForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES["excel_file"]
                try:
                    # Đọc file Excel sử dụng pandas
                    df = pd.read_excel(excel_file)

                    success_count = 0
                    error_count = 0
                    error_messages = []

                    # Duyệt qua từng dòng trong DataFrame
                    for index, row in df.iterrows():
                        try:
                            # Kiểm tra username, nếu không có thì tự tạo
                            username = row.get("username")
                            if not username:
                                username = self._generate_username(
                                    row.get("first_name", ""), row.get("last_name", "")
                                )
                            elif User.objects.filter(username=username).exists():
                                error_count += 1
                                error_messages.append(
                                    f"Dòng {index+2}: Username '{username}' đã tồn tại."
                                )
                                continue

                            # Tạo user mới
                            user = User(
                                username=username,
                                email=row.get("email", ""),
                                first_name=row.get("first_name", ""),
                                last_name=row.get("last_name", ""),
                                role=row.get("role", "student"),
                                phone_number=row.get("phone_number", ""),
                                address=row.get("address", ""),
                                is_active=row.get("is_active", True),
                            )

                            # Xử lý ngày sinh nếu có
                            date_of_birth = row.get("date_of_birth")
                            if date_of_birth:
                                user.date_of_birth = date_of_birth

                            # Đặt mật khẩu mặc định
                            user.set_password(get_default_password(user))
                            user.save()
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            error_messages.append(f"Dòng {index+2}: {str(e)}")

                    # Hiển thị thông báo kết quả
                    self.message_user(
                        request,
                        _(
                            f"Đã tạo thành công {success_count} tài khoản. Có {error_count} lỗi."
                        ),
                    )
                    for error in error_messages:
                        messages.error(request, error)

                    return redirect("admin:accounts_user_changelist")
                except Exception as e:
                    self.message_user(
                        request,
                        _(f"Lỗi khi xử lý file Excel: {str(e)}"),
                        level=messages.ERROR,
                    )

        form = ImportExcelForm()
        return render(
            request,
            "admin/accounts/user/import_excel.html",
            {
                "form": form,
                "title": _("Import người dùng từ Excel"),
            },
        )


admin.site.register(User, UserAdmin)


# Tùy chỉnh hiển thị Group trong Admin
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "get_permissions")
    search_fields = ("name",)
    filter_horizontal = ("permissions",)

    def get_permissions(self, obj):
        return ", ".join([p.codename for p in obj.permissions.all()[:10]])

    get_permissions.short_description = _("Danh sách quyền")


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# Đăng ký Permission để dễ dàng quản lý
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "codename")
    list_filter = ("content_type",)
    search_fields = ("name", "codename")


admin.site.register(Permission, PermissionAdmin)
