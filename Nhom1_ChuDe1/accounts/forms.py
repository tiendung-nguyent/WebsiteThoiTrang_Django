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
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(
                attrs={'placeholder': 'Nhập số điện thoại'}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Số điện thoại không được để trống.")
        # Dùng iexact để kiểm tra trùng lặp không phân biệt hoa thường, tránh lỗi IntegrityError
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Số điện thoại đã tồn tại.")
        return username

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp.")

        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        username = self.cleaned_data['username'].strip()
        user.username = username
        user.first_name = self.cleaned_data.get('custom_username', '').strip()
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            
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