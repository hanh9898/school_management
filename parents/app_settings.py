from django.conf import settings

# Các cài đặt mặc định cho app parents
parent_SETTINGS = {
    "allow_multiple_children": True,  # Cho phép một phụ huynh có nhiều con
    "require_primary_parent": True,  # Yêu cầu học sinh phải có ít nhất một phụ huynh chính
}

# Lấy cài đặt từ settings chính, nếu có
if hasattr(settings, "parent_SETTINGS"):
    parent_SETTINGS.update(settings.parent_SETTINGS)
