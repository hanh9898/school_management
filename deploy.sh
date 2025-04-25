#!/bin/bash

# Script triển khai đa năng cho School Management System
# Hỗ trợ các chế độ: docker, k8s, auto-deploy

# Hiển thị hướng dẫn sử dụng
show_help() {
    echo "Cách sử dụng: $0 [tùy chọn]"
    echo ""
    echo "Tùy chọn:"
    echo "  --help                  Hiển thị hướng dẫn này"
    echo ""
    echo "  --docker [profile]      Chạy với Docker Compose"
    echo "                          profile: default, debug, db-only (mặc định: default)"
    echo ""
    echo "  --k8s [env]             Triển khai lên Kubernetes"
    echo "                          env: dev, prod (mặc định: dev)"
    echo ""
    echo "  --auto-deploy [env]     Tự động build và deploy khi code thay đổi"
    echo "                          env: dev, prod (mặc định: dev)"
    echo ""
    echo "  --build [tag]           Chỉ build Docker image"
    echo "                          tag: latest, dev, prod (mặc định: latest)"
    echo ""
    echo "Ví dụ:"
    echo "  $0 --docker             # Chạy với Docker Compose (profile mặc định)"
    echo "  $0 --docker debug       # Chạy với Docker Compose (profile debug)"
    echo "  $0 --docker db-only     # Chỉ chạy cơ sở dữ liệu PostgreSQL"
    echo "  $0 --k8s dev            # Triển khai lên Kubernetes (môi trường dev)"
    echo "  $0 --auto-deploy        # Tự động build và deploy khi code thay đổi"
    echo "  $0 --build latest       # Chỉ build Docker image với tag 'latest'"
}

# Hàm để build Docker image
build_image() {
    local tag=${1:-latest}
    echo "Building Docker image: school-management:${tag}"
    docker build -t school-management:${tag} .

    # Nếu kind đã được cài đặt, load image vào cluster
    if command -v kind &> /dev/null; then
        if kind get clusters | grep -q school-management; then
            echo "Loading image into kind cluster: school-management:${tag}"
            kind load docker-image school-management:${tag} --name school-management
        fi
    fi

    echo "Build hoàn tất!"
}

# Hàm để triển khai lên Kubernetes
deploy_to_k8s() {
    local environment=${1:-dev}
    local namespace="school-management-${environment}"

    # Kiểm tra môi trường
    if [[ "${environment}" != "dev" && "${environment}" != "prod" ]]; then
        echo "Lỗi: Môi trường phải là 'dev' hoặc 'prod'"
        exit 1
    fi

    # Tạo namespace nếu chưa tồn tại
    kubectl create namespace ${namespace} --dry-run=client -o yaml | kubectl apply -f -

    # Cập nhật image trong kustomization.yaml
    sed -i.bak "s|newTag: ${environment}|newTag: latest|g" k8s/overlays/${environment}/kustomization.yaml
    rm -f k8s/overlays/${environment}/kustomization.yaml.bak

    # Tải biến môi trường từ file .env.{environment}
    if [ -f ".env.${environment}" ]; then
        echo "Đang tải biến môi trường từ file .env.${environment}..."
        source .env.${environment}
    else
        echo "Cảnh báo: Không tìm thấy file .env.${environment}. Sử dụng biến môi trường hiện tại."
    fi

    # Áp dụng cấu hình Kubernetes
    echo "Đang triển khai lên môi trường ${environment} trong namespace ${namespace}..."

    # Nếu là môi trường sản xuất, yêu cầu xác nhận
    if [ "${environment}" == "prod" ]; then
        echo "CẢNH BÁO: Bạn đang triển khai lên môi trường SẢN XUẤT."
        echo "Đảm bảo rằng các biến môi trường và secret đã được cấu hình đúng."
        read -p "Bạn có chắc chắn muốn tiếp tục? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Đã hủy triển khai."
            exit 1
        fi
    fi

    kubectl apply -k k8s/overlays/${environment} -n ${namespace}

    # Kiểm tra trạng thái của các pods
    echo "Đang đợi pods sẵn sàng..."
    kubectl wait --for=condition=ready pod --all -n ${namespace} --timeout=300s || true

    echo "Triển khai hoàn tất!"
    echo "Bạn có thể kiểm tra trạng thái triển khai với:"
    echo "  kubectl get all -n ${namespace}"

    # Thiết lập port-forward cho ứng dụng
    echo "Đang thiết lập port-forward cho ứng dụng..."
    echo "Bạn có thể truy cập ứng dụng tại http://localhost:8000"
    echo "Nhấn Ctrl+C để dừng port-forwarding"
    kubectl port-forward svc/${environment}-school-management -n ${namespace} 8000:80
}

# Hàm để chạy với Docker Compose
run_docker() {
    local profile=${1:-default}

    case $profile in
        default)
            echo "Chạy với Docker Compose (profile mặc định)..."
            docker-compose up -d
            ;;
        debug)
            echo "Chạy với Docker Compose (profile debug)..."
            docker-compose --profile debug up -d
            ;;
        db-only)
            echo "Chỉ chạy cơ sở dữ liệu PostgreSQL..."
            docker-compose --profile db-only up -d
            ;;
        *)
            echo "Lỗi: Profile không hợp lệ. Phải là 'default', 'debug', hoặc 'db-only'."
            exit 1
            ;;
    esac

    echo "Docker Compose đã khởi động!"

    if [ "$profile" != "db-only" ]; then
        echo "Bạn có thể truy cập ứng dụng tại http://localhost:8000"
    else
        echo "Cơ sở dữ liệu PostgreSQL đã sẵn sàng tại localhost:5432"
    fi
}

# Xử lý tham số dòng lệnh
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case $1 in
    --help)
        show_help
        ;;
    --docker)
        run_docker ${2:-default}
        ;;
    --k8s)
        deploy_to_k8s ${2:-dev}
        ;;
    --build)
        build_image ${2:-latest}
        ;;
    *)
        echo "Lỗi: Tùy chọn không hợp lệ."
        show_help
        exit 1
        ;;
esac
