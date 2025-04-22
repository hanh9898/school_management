from django.urls import path
from . import views

urlpatterns = [
    # Xác thực
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path(
        "password_reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    # Quản lý hồ sơ
    path("profile/", views.profile_view, name="profile"),
    path("profile/change_password/", views.change_password, name="change_password"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    # API và quản lý quyền
    path("api/permissions/", views.user_permissions, name="user_permissions"),
    path("permissions/request/", views.permission_request, name="permission_request"),
    # Admin user management
    path("admin-panel/users/", views.admin_user_list, name="admin_user_list"),
    path(
        "admin-panel/users/create/", views.admin_user_create, name="admin_user_create"
    ),
    path(
        "admin-panel/users/<int:user_id>/edit/",
        views.admin_user_edit,
        name="admin_user_edit",
    ),
    path(
        "admin-panel/users/<int:user_id>/toggle-active/",
        views.admin_user_toggle_active,
        name="admin_user_toggle_active",
    ),
]
