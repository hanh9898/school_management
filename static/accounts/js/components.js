/* JavaScript cho các thành phần UI dùng chung */

document.addEventListener('DOMContentLoaded', function() {
    // Xử lý đóng thông báo alerts tự động sau 5 giây
    function setupAutoCloseAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            setTimeout(function() {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                } else {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        });
    }

    // Xử lý xác nhận các hành động quan trọng
    function setupConfirmActions() {
        const confirmActions = document.querySelectorAll('[data-confirm]');
        confirmActions.forEach(function(element) {
            element.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }

    // Xử lý chọn tất cả checkbox
    function setupSelectAllCheckboxes() {
        const selectAllCheckboxes = document.querySelectorAll('[data-select-all]');
        selectAllCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                const targetSelector = this.getAttribute('data-select-all');
                const targetCheckboxes = document.querySelectorAll(targetSelector);
                const isChecked = this.checked;

                targetCheckboxes.forEach(function(targetCheckbox) {
                    targetCheckbox.checked = isChecked;
                });
            });
        });
    }

    // Xử lý hiển thị hình ảnh trước khi upload
    function setupImagePreview() {
        const avatarInput = document.getElementById('id_avatar');
        if (avatarInput) {
            avatarInput.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const previewImg = document.querySelector('.profile-img');
                        if (previewImg) {
                            previewImg.src = e.target.result;
                        }
                    }
                    reader.readAsDataURL(file);
                }
            });
        }
    }

    // Khởi tạo các chức năng
    setupAutoCloseAlerts();
    setupConfirmActions();
    setupSelectAllCheckboxes();
    setupImagePreview();
});