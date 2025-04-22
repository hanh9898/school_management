from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from accounts.permissions import sync_user_permissions, get_or_create_group, ROLE_GROUPS

class Command(BaseCommand):
    help = 'Đồng bộ quyền cho tất cả người dùng dựa trên vai trò'

    def handle(self, *args, **options):
        # Đảm bảo tất cả các nhóm đã được tạo
        for role, group_name in ROLE_GROUPS.items():
            group = get_or_create_group(role)
            self.stdout.write(self.style.SUCCESS(f'Đã tạo/cập nhật nhóm: {group_name}'))
        
        # Đồng bộ quyền cho tất cả người dùng
        users = User.objects.all()
        count = 0
        
        for user in users:
            sync_user_permissions(user)
            count += 1
            
            if count % 100 == 0:  # Log mỗi 100 người dùng
                self.stdout.write(f'Đã đồng bộ quyền cho {count} người dùng...')
        
        self.stdout.write(self.style.SUCCESS(f'Đã đồng bộ quyền thành công cho {count} người dùng'))
