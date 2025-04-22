from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.core.paginator import Paginator

from .models import User
from .forms.auth_forms import LoginForm, ProfileForm, UserAdminForm, UserCreateForm
from .utils import admin_required, get_default_password


# Views xác thực
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            remember_me = form.cleaned_data["remember_me"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Kiểm tra nếu người dùng là admin thì không cho vào admin Django
                if (
                    user.role == "admin"
                    and not user.is_superuser
                    and request.GET.get("next", "").startswith("/admin/")
                ):
                    messages.error(
                        request, _("Bạn không có quyền truy cập trang quản trị Django.")
                    )
                    return redirect("dashboard")

                login(request, user)

                if not remember_me:
                    request.session.set_expiry(0)  # Phiên hết hạn khi đóng trình duyệt

                # Chuyển hướng đến trang tiếp theo hoặc dashboard
                next_url = request.GET.get("next", reverse("dashboard"))
                if (
                    user.role == "admin"
                    and "/admin/" in next_url
                    and not user.is_superuser
                ):
                    next_url = reverse("dashboard")
                return redirect(next_url)
            else:
                messages.error(request, _("Tên đăng nhập hoặc mật khẩu không đúng."))
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, _("Bạn đã đăng xuất thành công."))
    return redirect("login")


# Quản lý hồ sơ
@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Thông tin hồ sơ đã được cập nhật."))
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # Giữ người dùng đăng nhập sau khi đổi mật khẩu
            messages.success(
                request, _("Mật khẩu của bạn đã được cập nhật thành công!")
            )
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


# Khôi phục mật khẩu
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(Q(email=email) & Q(is_active=True))

            if users.exists():
                for user in users:
                    subject = _("Yêu cầu đặt lại mật khẩu")
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))

                    reset_url = request.build_absolute_uri(
                        reverse(
                            "password_reset_confirm",
                            kwargs={"uidb64": uid, "token": token},
                        )
                    )

                    email_body = render_to_string(
                        "accounts/password_reset_email.html",
                        {
                            "user": user,
                            "reset_url": reset_url,
                        },
                    )

                    try:
                        send_mail(
                            subject,
                            email_body,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                        )
                        messages.success(
                            request,
                            _(
                                "Chúng tôi đã gửi hướng dẫn đặt lại mật khẩu đến email của bạn."
                            ),
                        )
                    except BadHeaderError:
                        messages.error(request, _("Có lỗi xảy ra khi gửi email."))

                    return redirect("login")
            else:
                messages.error(
                    request, _("Email không tồn tại hoặc tài khoản đã bị vô hiệu hóa.")
                )
    else:
        form = PasswordResetForm()

    return render(request, "accounts/password_reset.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    _(
                        "Mật khẩu của bạn đã được đặt lại thành công! Bạn có thể đăng nhập ngay bây giờ."
                    ),
                )
                return redirect("login")
        else:
            form = SetPasswordForm(user)

        return render(request, "accounts/password_reset_confirm.html", {"form": form})
    else:
        messages.error(
            request, _("Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.")
        )
        return redirect("password_reset")


# Dashboard theo vai trò
@login_required
def dashboard(request):
    user = request.user

    # Phân loại dashboard theo vai trò
    if user.is_admin:
        return render(request, "accounts/dashboard/admin_dashboard.html")
    elif user.is_teacher:
        return render(request, "accounts/dashboard/teacher_dashboard.html")
    elif user.is_parent:
        return render(request, "accounts/dashboard/parent_dashboard.html")
    elif user.is_student:
        return render(request, "accounts/dashboard/student_dashboard.html")
    else:
        # Dashboard mặc định
        return render(request, "accounts/dashboard/default_dashboard.html")


# API để lấy thông tin quyền của người dùng
@login_required
def user_permissions(request):
    user = request.user

    # Lấy tất cả quyền của người dùng
    permissions = user.get_all_permissions()

    # Lấy thông tin về các nhóm
    groups = [group.name for group in user.groups.all()]

    context = {
        "user_info": {
            "username": user.username,
            "email": user.email,
            "role": user.get_role_display(),
            "full_name": user.get_full_name(),
        },
        "permissions": list(permissions),
        "groups": groups,
    }

    return JsonResponse(context)


# Xem yêu cầu quyền
@login_required
def permission_request(request):
    if request.method == "POST":
        requested_permission = request.POST.get("permission")
        reason = request.POST.get("reason")

        # Lưu yêu cầu vào cơ sở dữ liệu (sẽ xây dựng model sau)
        # ...

        messages.success(
            request,
            _("Yêu cầu quyền đã được gửi. Chúng tôi sẽ xem xét và phản hồi sớm."),
        )
        return redirect("profile")

    # Lấy danh sách các quyền hiện có
    permissions = Permission.objects.all()

    return render(
        request, "accounts/permission_request.html", {"permissions": permissions}
    )


# Chức năng quản lý user cho Admin (không phải superadmin)
@admin_required
def admin_user_list(request):
    # Lọc theo role và trạng thái
    role_filter = request.GET.get("role", "")
    status_filter = request.GET.get("status", "")
    search_query = request.GET.get("q", "")

    # Lấy tất cả user ngoại trừ superuser và chính mình
    users = User.objects.exclude(is_superuser=True).exclude(id=request.user.id)

    # Quản trị viên chỉ có thể xem những user có role thấp hơn
    if request.user.role == "admin" and not request.user.is_superuser:
        users = users.exclude(role="admin")

    # Áp dụng các bộ lọc
    if role_filter:
        users = users.filter(role=role_filter)

    if status_filter:
        is_active = status_filter == "active"
        users = users.filter(is_active=is_active)

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    # Phân trang
    paginator = Paginator(users, 10)  # 10 users mỗi trang
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "accounts/admin/user_list.html",
        {
            "page_obj": page_obj,
            "role_filter": role_filter,
            "status_filter": status_filter,
            "search_query": search_query,
            "roles": User.ROLE_CHOICES,
        },
    )


@admin_required
def admin_user_create(request):

    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, _(f"Tài khoản {user.username} đã được tạo thành công.")
            )
            return redirect("admin_user_list")
    else:
        form = UserCreateForm()

    return render(
        request,
        "accounts/admin/user_create.html",
        {
            "form": form,
        },
    )


@admin_required
def admin_user_edit(request, user_id):

    user = get_object_or_404(User, id=user_id)

    # Không cho phép chỉnh sửa tài khoản admin khác hoặc superuser
    if (user.is_admin and not request.user.is_superuser) or user.is_superuser:
        messages.error(request, _("Bạn không có quyền chỉnh sửa tài khoản này."))
        return redirect("admin_user_list")

    if request.method == "POST":
        form = UserAdminForm(request.POST, instance=user)
        if form.is_valid():
            # Lưu thông tin người dùng
            user = form.save()

            # Xử lý yêu cầu đặt lại mật khẩu
            if form.cleaned_data.get("reset_password"):
                user.set_password(get_default_password(user))
                user.save(update_fields=["password"])
                messages.success(request, _("Mật khẩu đã được đặt lại thành công."))

            messages.success(
                request, _(f"Thông tin tài khoản {user.username} đã được cập nhật.")
            )
            return redirect("admin_user_list")
    else:
        form = UserAdminForm(instance=user)

    return render(
        request,
        "accounts/admin/user_edit.html",
        {
            "form": form,
            "user_obj": user,
        },
    )


@admin_required
def admin_user_toggle_active(request, user_id):

    user = get_object_or_404(User, id=user_id)

    # Không cho phép chỉnh sửa tài khoản admin khác hoặc superuser
    if (user.is_admin and not request.user.is_superuser) or user.is_superuser:
        messages.error(request, _("Bạn không có quyền chỉnh sửa tài khoản này."))
        return redirect("admin_user_list")

    # Đổi trạng thái active
    user.is_active = not user.is_active
    user.save()

    action = _("kích hoạt") if user.is_active else _("vô hiệu hóa")
    messages.success(request, _(f"Đã {action} tài khoản {user.username}."))

    return redirect("admin_user_list")
