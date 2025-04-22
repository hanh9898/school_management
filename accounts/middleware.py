from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class AdminAccessMiddleware:
    """
    Middleware để kiểm soát quyền truy cập vào trang admin của Django.
    Chỉ cho phép superuser truy cập vào trang admin của Django.
    Người dùng có role="admin" sẽ được chuyển hướng đến dashboard riêng của họ.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Kiểm tra nếu đường dẫn bắt đầu bằng /admin/ và không phải là /admin/login/
        if request.path.startswith("/admin/") and not request.path.startswith(
            "/admin/login/"
        ):
            # Nếu người dùng đã đăng nhập
            if request.user.is_authenticated:
                # Nếu không phải superuser
                if not request.user.is_superuser:
                    messages.warning(
                        request,
                        _("Bạn không có quyền truy cập trang quản trị Django."),
                    )
                    return redirect("dashboard")

        response = self.get_response(request)
        return response
