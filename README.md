# Hệ thống Quản lý Đào Tạo Trường Tiểu Học

Hệ thống quản lý toàn diện cho trường tiểu học, bao gồm quản lý học sinh, giáo viên, lớp học, điểm số, thời khóa biểu, tài liệu, và thông báo.

## Các tính năng chính

1. **Quản lý thông tin học sinh**
   - Hồ sơ học sinh, thông tin liên hệ, lịch sử học tập
   - Quản lý phụ huynh và mối quan hệ với học sinh

2. **Quản lý lớp học và thời khóa biểu**
   - Quản lý lớp học, phân bổ giáo viên
   - Lập thời khóa biểu và lịch kiểm tra

3. **Quản lý điểm số và đánh giá**
   - Nhập và quản lý điểm số
   - Tạo báo cáo học tập theo kỳ, năm học

4. **Quản lý giáo viên**
   - Hồ sơ giáo viên, chuyên môn, lịch giảng dạy

5. **Giao tiếp và thông báo**
   - Thông báo toàn trường/lớp/cá nhân
   - Tin nhắn giữa giáo viên-phụ huynh

6. **Quản lý tài liệu học tập**
   - Lưu trữ, phân loại và chia sẻ tài liệu

7. **Quản lý sự kiện và hoạt động ngoại khóa**
   - Lên lịch sự kiện, đăng ký tham gia

8. **Quản lý chuyên cần**
   - Điểm danh, báo cáo vắng mặt

## Phân quyền hệ thống

Hệ thống có 4 vai trò chính:

- **Admin**: Quản trị hệ thống, toàn quyền trên mọi chức năng
- **Giáo viên**: Quản lý lớp học, nhập điểm, gửi thông báo, tải tài liệu
- **Phụ huynh**: Xem thông tin con, nhận thông báo, liên hệ với giáo viên
- **Học sinh**: Xem điểm, thời khóa biểu, tài liệu học tập

## Cài đặt và Triển khai

### Yêu cầu hệ thống
- Python 3.13+
- Django 5.2+
- PostgreSQL
- Docker và Docker Compose (tùy chọn)
- Kubernetes (tùy chọn)
- Các thư viện trong file requirements.txt

### Cài đặt với Docker (Khuyến nghị)

1. Cài đặt Docker và Docker Compose:
   - [Hướng dẫn cài đặt Docker](https://docs.docker.com/get-docker/)
   - [Hướng dẫn cài đặt Docker Compose](https://docs.docker.com/compose/install/)

2. Sao chép file .env.example thành .env và điều chỉnh các biến môi trường:
   ```bash
   cp .env.example .env
   ```

3. Xây dựng và khởi chạy các container:
   ```bash
   ./deploy.sh --docker
   ```

4. Tạo tài khoản quản trị:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Đồng bộ quyền cho người dùng:
   ```bash
   docker-compose exec web python manage.py sync_permissions
   ```

6. Truy cập hệ thống:
   - Trang quản trị: http://localhost:8000/admin/
   - Trang chủ: http://localhost:8000/

### Cài đặt với Docker cho Debug

Để debug ứng dụng trong Docker, sử dụng profile debug:

```bash
./deploy.sh --docker debug
```

Profile này cấu hình debugpy để cho phép debug từ xa qua cổng 5678.

### Cài đặt với Kubernetes

Dự án này hỗ trợ triển khai trên Kubernetes. Xem thêm hướng dẫn chi tiết trong thư mục [k8s/README.md](k8s/README.md).

1. Cài đặt Kind (Kubernetes in Docker):
   ```bash
   brew install kind
   kind create cluster --name school-management --config kind-config.yaml
   ```

2. Sử dụng script `deploy.sh` để triển khai ứng dụng:

   ```bash
   # Build Docker image
   ./deploy.sh --build latest

   # Triển khai lên môi trường phát triển
   ./deploy.sh --k8s dev

   # Hoặc tự động build và deploy khi code thay đổi
   ./deploy.sh --auto-deploy
   ```

   Xem thêm hướng dẫn chi tiết trong [deploy.md](deploy.md)

3. Truy cập ứng dụng:
   - Thêm dòng sau vào file `/etc/hosts`:
     ```
     127.0.0.1   school-management.com
     ```
   - Truy cập: http://school-management.com

### Cài đặt môi trường phát triển thông thường

1. Tạo và kích hoạt môi trường ảo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

2. Cài đặt các thư viện:
   ```bash
   pip install -r requirements.txt
   ```

3. Sao chép file .env.example thành .env và điều chỉnh các biến môi trường:
   ```bash
   cp .env.example .env
   ```

4. Thiết lập cơ sở dữ liệu:
   ```bash
   python manage.py migrate
   ```

5. Tạo tài khoản quản trị:
   ```bash
   python manage.py createsuperuser
   ```

6. Đồng bộ quyền cho người dùng:
   ```bash
   python manage.py sync_permissions
   ```

7. Chạy ứng dụng:
   ```bash
   python manage.py runserver
   ```

8. Truy cập hệ thống:
   - Trang quản trị: http://localhost:8000/admin/
   - Trang chủ: http://localhost:8000/

## Tác giả
Được phát triển bởi Hanhnt