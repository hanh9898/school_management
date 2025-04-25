# Hướng dẫn sử dụng Script Triển khai

## Quản lý Secret và Biến Môi Trường

Script này hỗ trợ việc quản lý secret và biến môi trường theo từng môi trường cụ thể:

- **Môi trường phát triển (dev)**: Sử dụng file `.env.dev`
- **Môi trường sản xuất (prod)**: Sử dụng file `.env.prod`

Khi triển khai lên Kubernetes, script sẽ tự động tải các biến môi trường từ file tương ứng và sử dụng chúng để tạo các secret.

## Yêu cầu

- Docker và Docker Compose đã được cài đặt
- Kubernetes (kubectl) đã được cài đặt (cho chế độ k8s)
- Kind đã được cài đặt (cho chế độ k8s)

## Cách sử dụng

```bash
./deploy.sh [tùy chọn]
```

### Các tùy chọn

#### Hiển thị hướng dẫn

```bash
./deploy.sh --help
```

#### Chạy với Docker Compose

```bash
# Chạy với profile mặc định
./deploy.sh --docker

# Chạy với profile debug (cho phép debug từ xa)
./deploy.sh --docker debug

# Chỉ chạy cơ sở dữ liệu PostgreSQL
./deploy.sh --docker db-only
```

#### Triển khai lên Kubernetes

```bash
# Triển khai lên môi trường phát triển (dev)
./deploy.sh --k8s dev

# Triển khai lên môi trường sản xuất (prod)
./deploy.sh --k8s prod
```

#### Chỉ build Docker image

```bash
# Build image với tag 'latest'
./deploy.sh --build

# Build image với tag cụ thể
./deploy.sh --build dev
./deploy.sh --build prod
```

## Chi tiết các chế độ

### Chế độ Docker

Chế độ Docker sử dụng Docker Compose để chạy ứng dụng và cơ sở dữ liệu. Có ba profile có sẵn:

- **default**: Chạy ứng dụng Django và cơ sở dữ liệu PostgreSQL
- **debug**: Chạy ứng dụng Django với debugpy và cơ sở dữ liệu PostgreSQL
- **db-only**: Chỉ chạy cơ sở dữ liệu PostgreSQL

### Chế độ Kubernetes

Chế độ Kubernetes triển khai ứng dụng lên cluster Kubernetes. Script sẽ:

1. Tạo namespace nếu chưa tồn tại
2. Cập nhật tag trong kustomization.yaml
3. Tải biến môi trường từ file `.env.{environment}`
4. Áp dụng cấu hình Kubernetes, bao gồm các secret
5. Thiết lập port-forward để truy cập ứng dụng

Khi triển khai lên môi trường sản xuất (prod), script sẽ yêu cầu xác nhận để đảm bảo bạn đã cấu hình đúng các biến môi trường và secret.

## Xử lý sự cố

### Docker Compose không khởi động

```bash
# Kiểm tra logs
docker-compose logs

# Dừng và xóa tất cả container
docker-compose down
```

### Kubernetes deployment không hoạt động

```bash
# Kiểm tra pods
kubectl get pods -n school-management-dev

# Xem logs của pod
kubectl logs <pod-name> -n school-management-dev
```

## Dừng các dịch vụ

### Dừng Docker Compose

```bash
docker-compose down
```
