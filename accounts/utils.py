from django.utils.translation import gettext_lazy as _
import unicodedata
import re
from unidecode import unidecode
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import User


def generate_username_from_name(first_name, last_name):
    """
    Tạo username từ họ tên không dấu.
    Kiểm tra trùng lặp và thêm số nếu cần.

    Args:
        first_name (str): Tên
        last_name (str): Họ

    Returns:
        str: Username được tạo
    """
    # Tạo username từ tên không dấu
    full_name = f"{first_name}{last_name}".lower()

    # Xử lý bỏ dấu (sử dụng unidecode nếu có, nếu không thì dùng unicodedata)
    try:
        base_username = unidecode(full_name).replace(" ", "")
    except:
        # Fallback nếu không có unidecode
        full_name = (
            unicodedata.normalize("NFKD", full_name)
            .encode("ASCII", "ignore")
            .decode("utf-8")
        )
        base_username = re.sub(r"[^\w]", "", full_name)

    # Kiểm tra trùng và thêm số nếu cần
    username = base_username
    count = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{count}"
        count += 1

    return username


def get_default_password(user):
    """
    Tạo mật khẩu mặc định dựa trên ngày sinh hoặc username.

    Args:
        user (User): Đối tượng người dùng

    Returns:
        str: Mật khẩu mặc định
    """
    if user.date_of_birth:
        return user.date_of_birth.strftime("%d%m%Y")
    else:
        return user.username


def admin_required(view_func):
    """
    Decorator để kiểm tra quyền admin.
    Nếu người dùng không phải admin hoặc superuser thì chuyển hướng về dashboard.
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin and not request.user.is_superuser:
            messages.error(request, _("Bạn không có quyền truy cập trang này."))
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper
