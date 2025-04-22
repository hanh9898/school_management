from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from ..models import User
from .mixins import DateOfBirthFormMixin
from ..utils import generate_username_from_name, get_default_password


class LoginForm(forms.Form):
    username = forms.CharField(label=_("Tên đăng nhập"), max_length=100)
    password = forms.CharField(label=_("Mật khẩu"), widget=forms.PasswordInput)
    remember_me = forms.BooleanField(label=_("Ghi nhớ đăng nhập"), required=False)


class ProfileForm(DateOfBirthFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "date_of_birth",
            "avatar",
        ]


class UserAdminForm(DateOfBirthFormMixin, forms.ModelForm):
    """Form sử dụng cho admin để quản lý user"""

    is_active = forms.BooleanField(label=_("Kích hoạt"), required=False)
    reset_password = forms.BooleanField(
        label=_("Đặt lại mật khẩu"),
        required=False,
        help_text=_("Đặt lại mật khẩu về mặc định (ngày sinh hoặc username)"),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "phone_number",
            "address",
            "date_of_birth",
            "is_active",
            "groups",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Người dùng Admin không thể nâng cấp người khác lên Admin
        role_choices = [
            (role, label)
            for role, label in self.fields["role"].choices
            if role != "admin"
        ]
        self.fields["role"].choices = role_choices


class UserCreateForm(DateOfBirthFormMixin, UserCreationForm):
    """Form tạo user mới cho admin"""

    username = forms.CharField(
        label=_("Tên đăng nhập"),  # Thêm text trực tiếp vào label
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
        help_text="",
    )

    password1 = forms.CharField(
        label=_("Mật khẩu"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        required=False,
        help_text="",
    )
    password2 = forms.CharField(
        label=_("Xác nhận mật khẩu"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False,
        help_text="",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone_number",
            "address",
            "date_of_birth",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bỏ đi các validation message mặc định
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name", "")
        last_name = cleaned_data.get("last_name", "")

        if not cleaned_data.get("username"):
            # Sử dụng hàm tiện ích để tạo username
            cleaned_data["username"] = generate_username_from_name(
                first_name, last_name
            )

        # Bỏ qua validation password
        cleaned_data["password1"] = "temp_password"
        cleaned_data["password2"] = "temp_password"

        return cleaned_data

    def _post_clean(self):
        # Ghi đè phương thức này để bỏ qua validation password
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        # Sử dụng hàm tiện ích để đặt mật khẩu mặc định
        user.set_password(get_default_password(user))

        if commit:
            user.save()

        return user
