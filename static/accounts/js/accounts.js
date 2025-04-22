/* JavaScript cho module accounts */

document.addEventListener('DOMContentLoaded', function() {
    // Khởi tạo tooltips nếu có
    function setupTooltips() {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        if (typeof bootstrap !== 'undefined') {
            [...tooltipTriggerList].forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
        }
    }

    // Xử lý toggle mật khẩu cho form đăng nhập
    function setupPasswordToggle() {
        const togglePasswordButtons = document.querySelectorAll('.toggle-password');
        togglePasswordButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                const passwordField = document.querySelector(this.getAttribute('data-target'));
                if (passwordField) {
                    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordField.setAttribute('type', type);

                    // Đổi icon
                    const icon = this.querySelector('i');
                    if (icon) {
                        if (type === 'text') {
                            icon.classList.remove('fa-eye');
                            icon.classList.add('fa-eye-slash');
                        } else {
                            icon.classList.remove('fa-eye-slash');
                            icon.classList.add('fa-eye');
                        }
                    }
                }
            });
        });
    }

    // Khởi tạo các chức năng
    setupTooltips();
    setupPasswordToggle();
});