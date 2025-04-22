from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _

# Định nghĩa quyền mặc định cho từng vai trò
ROLE_PERMISSIONS = {
    "admin": [
        # Quyền quản lý người dùng
        "view_user",
        "add_user",
        "change_user",
        "delete_user",
        # Quyền quản lý học sinh
        "view_student_info",
        "edit_student_info",
        # Quyền quản lý điểm số
        "view_grades",
        "edit_grades",
        # Quyền quản lý điểm danh
        "view_attendance",
        "edit_attendance",
        # Quyền quản lý thời khóa biểu
        "view_timetable",
        "edit_timetable",
    ],
    "teacher": [
        # Quyền xem thông tin học sinh
        "view_student_info",
        # Quyền quản lý điểm số
        "view_grades",
        "edit_grades",
        # Quyền quản lý điểm danh
        "view_attendance",
        "edit_attendance",
        # Quyền xem thời khóa biểu
        "view_timetable",
    ],
    "parent": [
        # Quyền xem thông tin con
        "view_student_info",
        # Quyền xem điểm số
        "view_grades",
        # Quyền xem điểm danh
        "view_attendance",
        # Quyền xem thời khóa biểu
        "view_timetable",
    ],
    "student": [
        # Quyền xem thông tin cá nhân
        "view_student_info",
        # Quyền xem điểm số
        "view_grades",
        # Quyền xem điểm danh
        "view_attendance",
        # Quyền xem thời khóa biểu
        "view_timetable",
    ],
}

# Tên nhóm cho từng vai trò
ROLE_GROUPS = {
    "admin": "Administrators",
    "teacher": "Teachers",
    "parent": "Parents",
    "student": "Students",
}


def get_or_create_group(role):
    """
    Lấy hoặc tạo nhóm cho vai trò.

    Args:
        role (str): Vai trò của người dùng

    Returns:
        Group: Đối tượng nhóm
    """
    if role not in ROLE_GROUPS:
        return None

    group_name = ROLE_GROUPS[role]
    group, created = Group.objects.get_or_create(name=group_name)

    # Nếu nhóm mới được tạo, gán quyền mặc định
    if created:
        assign_permissions_to_group(group, role)

    return group


def assign_permissions_to_group(group, role):
    """
    Gán quyền mặc định cho nhóm dựa trên vai trò.

    Args:
        group (Group): Đối tượng nhóm
        role (str): Vai trò của người dùng
    """
    if role not in ROLE_PERMISSIONS:
        return

    # Lấy danh sách quyền mặc định cho vai trò
    permission_codenames = ROLE_PERMISSIONS[role]

    # Lấy tất cả quyền hiện có
    permissions = Permission.objects.filter(codename__in=permission_codenames)

    # Gán quyền cho nhóm
    group.permissions.add(*permissions)


def assign_user_to_groups(user):
    """
    Gán người dùng vào nhóm dựa trên vai trò.

    Args:
        user: Đối tượng người dùng
    """
    # Xóa người dùng khỏi tất cả các nhóm hiện tại
    user.groups.clear()

    # Lấy hoặc tạo nhóm cho vai trò hiện tại
    group = get_or_create_group(user.role)
    if group:
        user.groups.add(group)


def sync_user_permissions(user):
    """
    Đồng bộ quyền của người dùng dựa trên vai trò.

    Args:
        user: Đối tượng người dùng
    """
    # Gán người dùng vào nhóm tương ứng
    assign_user_to_groups(user)
