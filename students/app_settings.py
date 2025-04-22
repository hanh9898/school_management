from django.conf import settings

# Các cài đặt mặc định cho app students
student_SETTINGS = {
    "allow_multiple_parents": True,  # Cho phép một học sinh có nhiều phụ huynh
    "auto_create_id": True,  # Tự động tạo mã học sinh khi tạo mới
    "student_id_prefix": "HS",  # Tiền tố cho mã học sinh
    "student_id_length": 6,  # Độ dài của mã học sinh (không bao gồm tiền tố)
}

# Lấy cài đặt từ settings chính, nếu có
if hasattr(settings, "student_SETTINGS"):
    student_SETTINGS.update(settings.student_SETTINGS)
