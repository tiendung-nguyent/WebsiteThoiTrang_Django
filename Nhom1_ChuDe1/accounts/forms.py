from django import forms
from django.contrib.auth.models import User
from quanLyKhachHang.models import KhachHang

class UserRegistrationForm(forms.ModelForm):
    custom_username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={'placeholder': 'Nhập tên đăng nhập tùy ý'}
        )
    )
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={'placeholder': 'Nhập họ và tên'}
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'placeholder': 'Nhập địa chỉ email'}
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Nhập mật khẩu (8-12 ký tự)'}
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Nhập lại mật khẩu'}
        )
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean_custom_username(self):
        custom_username = self.cleaned_data.get('custom_username', '').strip()
        if not custom_username:
            raise forms.ValidationError("Tên đăng nhập không được để trống.")
        if User.objects.filter(username__iexact=custom_username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại.")
        return custom_username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("Email không được để trống.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email đã được sử dụng.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp.")

        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].strip()
        user.email = email
        user.username = self.cleaned_data['custom_username'].strip()
        user.first_name = self.cleaned_data.get('full_name', '').strip()
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            
            # Ánh xạ vào Profile theo yêu cầu
            from accounts.models import Profile
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'full_name': self.cleaned_data.get('full_name', '').strip(),
                    'address': email
                }
            )
            
            # Tạo KhachHang liên kết với User mới tạo
            kh_ma = f"KH{user.id:07d}"
            full_name = self.cleaned_data.get('full_name', '').strip()
            kh, created = KhachHang.objects.get_or_create(
                KH_Ma=kh_ma,
                defaults={
                    'KH_Ten': full_name,
                    'KH_TongChiTieu': 0,
                    'KH_SoDonHang': 0
                }
            )
            
            # Nếu bản ghi đã tồn tại (do bị đụng độ với ID Khach le trước đó), ép cập nhật lại tên đúng
            if not created and kh.KH_Ten == 'Khach le':
                kh.KH_Ten = full_name
                kh.save()

        return user