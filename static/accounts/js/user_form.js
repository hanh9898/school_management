document.addEventListener('DOMContentLoaded', function() {
    // Avatar preview
    const avatarInput = document.getElementById('id_avatar');
    const avatarPreview = document.getElementById('avatar-preview');
    
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    if (avatarPreview.tagName === 'IMG') {
                        avatarPreview.src = e.target.result;
                    } else {
                        avatarPreview.innerHTML = `<img src="${e.target.result}" alt="Avatar Preview">`;
                    }
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Clear avatar (edit mode)
    const avatarClear = document.getElementById('avatar-clear');
    if (avatarClear) {
        avatarClear.addEventListener('click', function() {
            avatarInput.value = '';
            // Đường dẫn sẽ được đặt trong data attribute của phần tử
            avatarPreview.src = avatarPreview.getAttribute('data-default-avatar');
        });
    }
    
    // Role selection - edit mode
    const handleEditModeRoles = function() {
        const roleOptions = document.querySelectorAll('.role-option');
        const roleInput = document.getElementById('id_role');
        const studentInfo = document.getElementById('student-info');
        const teacherInfo = document.getElementById('teacher-info');
        
        roleOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Clear selection for all options
                roleOptions.forEach(opt => opt.classList.remove('selected'));
                
                // Add selected to current option
                this.classList.add('selected');
                
                // Update role value
                const role = this.getAttribute('data-role');
                roleInput.value = role;
                
                // Toggle role-specific info
                if (role === 'student') {
                    studentInfo.style.display = 'block';
                    teacherInfo.style.display = 'none';
                } else if (role === 'teacher') {
                    studentInfo.style.display = 'none';
                    teacherInfo.style.display = 'block';
                } else {
                    studentInfo.style.display = 'none';
                    teacherInfo.style.display = 'none';
                }
            });
        });
    };
    
    // Role selection - create mode
    const handleCreateModeRoles = function() {
        const roleOptions = document.querySelectorAll('.role-option');
        const roleInputs = document.querySelectorAll('.role-option input[type="radio"]');
        const studentInfo = document.getElementById('student-info');
        const teacherInfo = document.getElementById('teacher-info');
        
        // Initial state
        roleInputs.forEach(input => {
            if (input.checked) {
                input.closest('.role-option').classList.add('selected');
            }
        });
        
        roleOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Clear selection for all options
                roleOptions.forEach(opt => opt.classList.remove('selected'));
                
                // Add selected to current option
                this.classList.add('selected');
                
                // Check radio button
                const radio = this.querySelector('input[type="radio"]');
                radio.checked = true;
                
                // Toggle role-specific info if available
                if (studentInfo && teacherInfo) {
                    const role = radio.value;
                    if (role === 'student') {
                        studentInfo.style.display = 'block';
                        teacherInfo.style.display = 'none';
                    } else if (role === 'teacher') {
                        studentInfo.style.display = 'none';
                        teacherInfo.style.display = 'block';
                    } else {
                        studentInfo.style.display = 'none';
                        teacherInfo.style.display = 'none';
                    }
                }
            });
        });
    };
    
    // Kiểm tra xem đang ở chế độ chỉnh sửa hay tạo mới
    const userForm = document.getElementById('user-edit-form');
    if (userForm) {
        // Edit mode
        handleEditModeRoles();
    } else {
        // Create mode
        handleCreateModeRoles();
    }
    
    // Password toggle
    const togglePassword1 = document.getElementById('password-toggle1');
    const togglePassword2 = document.getElementById('password-toggle2');
    const passwordField1 = document.getElementById('id_password1');
    const passwordField2 = document.getElementById('id_password2');
    
    if (togglePassword1 && passwordField1) {
        togglePassword1.addEventListener('click', function() {
            const type = passwordField1.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField1.setAttribute('type', type);
            togglePassword1.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }
    
    if (togglePassword2 && passwordField2) {
        togglePassword2.addEventListener('click', function() {
            const type = passwordField2.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField2.setAttribute('type', type);
            togglePassword2.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }
    
    // Generate password
    const generatePasswordBtn = document.getElementById('generate-password-btn');
    
    if (generatePasswordBtn && passwordField1 && passwordField2) {
        generatePasswordBtn.addEventListener('click', function() {
            const length = 12;
            const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+=";
            let password = "";
            
            for (let i = 0; i < length; i++) {
                const randomIndex = Math.floor(Math.random() * charset.length);
                password += charset[randomIndex];
            }
            
            passwordField1.value = password;
            passwordField2.value = password;
            
            // Show password temporarily
            passwordField1.setAttribute('type', 'text');
            passwordField2.setAttribute('type', 'text');
            togglePassword1.innerHTML = '<i class="fas fa-eye-slash"></i>';
            togglePassword2.innerHTML = '<i class="fas fa-eye-slash"></i>';
            
            // Hide after 5 seconds
            setTimeout(function() {
                passwordField1.setAttribute('type', 'password');
                passwordField2.setAttribute('type', 'password');
                togglePassword1.innerHTML = '<i class="fas fa-eye"></i>';
                togglePassword2.innerHTML = '<i class="fas fa-eye"></i>';
            }, 5000);
        });
    }
}); 