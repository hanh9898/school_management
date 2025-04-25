# Triển khai School Management System trên Kubernetes

Tài liệu này hướng dẫn cách triển khai ứng dụng School Management System trên Kubernetes, bao gồm cả cách thiết lập môi trường phát triển với tính năng tự động cập nhật khi code thay đổi.

## Cấu trúc thư mục

```
k8s/
├── base/                  # Cấu hình cơ bản cho tất cả môi trường
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── django-deployment.yaml
│   ├── django-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── persistent-volume-claims.yaml
│   ├── ingress.yaml
│   └── kustomization.yaml
└── overlays/              # Cấu hình riêng cho từng môi trường
    ├── dev/               # Môi trường phát triển
    │   ├── kustomization.yaml
    │   └── patches/
    │       ├── configmap.yaml
    │       └── django-deployment.yaml
    └── prod/              # Môi trường sản xuất
        ├── kustomization.yaml
        └── patches/
            ├── configmap.yaml
            ├── django-deployment.yaml
            └── ingress.yaml
```

## Yêu cầu

- Kubernetes cluster (minikube, kind, hoặc cloud provider như GKE, EKS, AKS)
- kubectl đã được cài đặt và cấu hình
- Docker đã được cài đặt (để build image)
- kustomize đã được cài đặt (tùy chọn, kubectl đã tích hợp kustomize)
- fswatch (cho tính năng auto-deploy trong môi trường phát triển)

## Thiết lập môi trường

### 1. Cài đặt Kind (Kubernetes in Docker)

```bash
# Cài đặt Kind
brew install kind

# Tạo cluster
kind create cluster --name school-management --config kind-config.yaml
```

Nội dung file `kind-config.yaml`:
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
```

### 2. Cài đặt các công cụ cần thiết

```bash
# Cài đặt kubectl
brew install kubectl

# Cài đặt fswatch (cho tính năng auto-deploy)
brew install fswatch
```

## Các bước triển khai

Sử dụng script `deploy.sh` để triển khai ứng dụng lên Kubernetes. Script này hỗ trợ nhiều chế độ triển khai khác nhau.

### Triển khai thủ công

```bash
# Cấp quyền thực thi cho script
chmod +x deploy.sh

# Build Docker image
./deploy.sh --build latest

# Triển khai lên môi trường phát triển
./deploy.sh --k8s dev

# Triển khai lên môi trường sản xuất
./deploy.sh --k8s prod
```

### Triển khai tự động (Auto-deploy)

Script `deploy.sh` cũng hỗ trợ chế độ tự động build và deploy lại ứng dụng khi code thay đổi:

```bash
# Tự động build và deploy lên môi trường phát triển
./deploy.sh --auto-deploy

# Tự động build và deploy lên môi trường sản xuất
./deploy.sh --auto-deploy prod
```

Chi tiết về cách sử dụng script này có thể xem trong file [deploy.md](../deploy.md).

### Triển khai thủ công (không sử dụng script)

Nếu bạn muốn triển khai thủ công mà không sử dụng script, bạn có thể thực hiện các bước sau:

#### 1. Build Docker image

```bash
# Build image từ Dockerfile
docker build -t school-management:latest .

# Load image vào Kind cluster
kind load docker-image school-management:latest --name school-management
```

#### 2. Tạo namespace

```bash
# Tạo namespace cho môi trường phát triển
kubectl create namespace school-management-dev

# Tạo namespace cho môi trường sản xuất
kubectl create namespace school-management-prod
```

#### 3. Triển khai lên Kubernetes

```bash
# Triển khai lên môi trường phát triển
kubectl apply -k k8s/overlays/dev -n school-management-dev

# Triển khai lên môi trường sản xuất
kubectl apply -k k8s/overlays/prod -n school-management-prod
```

### 4. Kiểm tra trạng thái triển khai

```bash
# Kiểm tra môi trường phát triển
kubectl get all -n school-management-dev

# Kiểm tra môi trường sản xuất
kubectl get all -n school-management-prod
```

### 5. Truy cập ứng dụng

Để truy cập ứng dụng từ máy local, thêm dòng sau vào file `/etc/hosts`:

```
127.0.0.1   school-management.com
```

Sau đó, bạn có thể truy cập ứng dụng tại:

```
http://school-management.com
```

## Quản lý cơ sở dữ liệu

### Tạo superuser

```bash
# Môi trường phát triển
kubectl exec -it $(kubectl get pods -l app=school-management -n school-management-dev -o jsonpath="{.items[0].metadata.name}") -n school-management-dev -- python manage.py createsuperuser

# Môi trường sản xuất
kubectl exec -it $(kubectl get pods -l app=school-management -n school-management-prod -o jsonpath="{.items[0].metadata.name}") -n school-management-prod -- python manage.py createsuperuser
```

### Đồng bộ quyền

```bash
# Môi trường phát triển
kubectl exec -it $(kubectl get pods -l app=school-management -n school-management-dev -o jsonpath="{.items[0].metadata.name}") -n school-management-dev -- python manage.py sync_permissions

# Môi trường sản xuất
kubectl exec -it $(kubectl get pods -l app=school-management -n school-management-prod -o jsonpath="{.items[0].metadata.name}") -n school-management-prod -- python manage.py sync_permissions
```

### Sao lưu và khôi phục dữ liệu

```bash
# Sao lưu dữ liệu từ môi trường phát triển
kubectl exec -it $(kubectl get pods -l app=postgres -n school-management-dev -o jsonpath="{.items[0].metadata.name}") -n school-management-dev -- pg_dump -U postgres -d school_management > backup.sql

# Khôi phục dữ liệu vào môi trường phát triển
cat backup.sql | kubectl exec -i $(kubectl get pods -l app=postgres -n school-management-dev -o jsonpath="{.items[0].metadata.name}") -n school-management-dev -- psql -U postgres -d school_management
```

## Xử lý sự cố

### Xem logs

```bash
# Xem logs của ứng dụng Django
kubectl logs -l app=school-management -n school-management-dev
kubectl logs -l app=school-management -n school-management-prod

# Xem logs của PostgreSQL
kubectl logs -l app=postgres -n school-management-dev
kubectl logs -l app=postgres -n school-management-prod

# Theo dõi logs theo thời gian thực
kubectl logs -f -l app=school-management -n school-management-dev
```

### Truy cập shell của container

```bash
# Truy cập shell của container Django
kubectl exec -it $(kubectl get pods -l app=school-management -n school-management-dev -o jsonpath="{.items[0].metadata.name}") -n school-management-dev -- sh
kubectl exec -it $(kubectl get pods -l app=school-management -n school-management-prod -o jsonpath="{.items[0].metadata.name}") -n school-management-prod -- sh

# Truy cập shell của container PostgreSQL
kubectl exec -it $(kubectl get pods -l app=postgres -n school-management-dev -o jsonpath="{.items[0].metadata.name}") -n school-management-dev -- sh
kubectl exec -it $(kubectl get pods -l app=postgres -n school-management-prod -o jsonpath="{.items[0].metadata.name}") -n school-management-prod -- sh
```

### Kiểm tra cấu hình

```bash
# Xem ConfigMap
kubectl get configmap -n school-management-dev
kubectl describe configmap dev-school-management-config -n school-management-dev

# Xem Secret
kubectl get secret -n school-management-dev
kubectl describe secret dev-school-management-secret -n school-management-dev

# Xem Ingress
kubectl get ingress -n school-management-dev
kubectl describe ingress dev-school-management-ingress -n school-management-dev
```

### Khởi động lại deployment

```bash
# Khởi động lại deployment Django
kubectl rollout restart deployment dev-school-management -n school-management-dev

# Khởi động lại deployment PostgreSQL
kubectl rollout restart deployment dev-postgres -n school-management-dev

# Kiểm tra trạng thái rollout
kubectl rollout status deployment dev-school-management -n school-management-dev
```

## Các vấn đề thường gặp và cách giải quyết

### 1. Pod không khởi động

Kiểm tra logs:
```bash
kubectl describe pod -l app=school-management -n school-management-dev
kubectl logs -l app=school-management -n school-management-dev
```

### 2. Không thể kết nối đến cơ sở dữ liệu

Kiểm tra service và endpoint:
```bash
kubectl get service -n school-management-dev
kubectl get endpoints -n school-management-dev
```

Kiểm tra logs của PostgreSQL:
```bash
kubectl logs -l app=postgres -n school-management-dev
```

### 3. Ingress không hoạt động

Kiểm tra cấu hình Ingress:
```bash
kubectl get ingress -n school-management-dev
kubectl describe ingress dev-school-management-ingress -n school-management-dev
```

Kiểm tra file `/etc/hosts`:
```
127.0.0.1   school-management.com
```

### 4. Thay đổi code không được cập nhật

Nếu bạn đang sử dụng script `auto-deploy.sh` nhưng thay đổi code không được cập nhật:

1. Kiểm tra xem script có đang chạy không:
```bash
ps aux | grep auto-deploy
```

2. Thử build lại image mà không sử dụng cache:
```bash
docker build --no-cache -t school-management:latest .
kind load docker-image school-management:latest --name school-management
kubectl rollout restart deployment dev-school-management -n school-management-dev
```

3. Kiểm tra logs để xem có lỗi nào không:
```bash
kubectl logs -l app=school-management -n school-management-dev
```
