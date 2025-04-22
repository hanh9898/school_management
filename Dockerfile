FROM python:3.13-alpine
# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các gói phụ thuộc
RUN apk update \
    && apk add --no-cache \
        postgresql-client \
        build-base \
        postgresql-dev \
        musl-dev

# Cài đặt các gói Python
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Sao chép mã nguồn
COPY . /app/

# Tạo thư mục cho static và media files
RUN mkdir -p /app/staticfiles /app/media

# Thiết lập người dùng không phải root
RUN adduser -D appuser
RUN chown -R appuser:appuser /app
USER appuser

# Mở cổng
EXPOSE 8000
EXPOSE 5678

# Chạy ứng dụng
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "school_management.wsgi:application"]
