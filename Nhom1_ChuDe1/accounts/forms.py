from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
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

    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={'placeholder': 'Nhập họ và tên'}
        )
    )

    gender = forms.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        widget=forms.RadioSelect
    )

    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'}
        )
    )

    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={'placeholder': '0123456789'}
        )
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Nhập địa chỉ',
                'rows': 3
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(
                attrs={'placeholder': 'Tên đăng nhập'}
            ),
            'email': forms.EmailInput(
                attrs={'placeholder': 'example@gmail.com'}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Tên đăng nhập không được để trống.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã được sử dụng.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp.")

        return confirm_password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '').strip()

        if not phone_number:
            raise forms.ValidationError("Số điện thoại không được để trống.")

        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Số điện thoại đã được sử dụng.")

        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username'].strip()
        user.email = self.cleaned_data['email'].strip()
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            Profile.objects.create(
                user=user,
                gender=self.cleaned_data['gender'],
                birth_date=self.cleaned_data['birth_date'],
                phone_number=self.cleaned_data['phone_number'],
                full_name=self.cleaned_data['full_name'],
                address=self.cleaned_data['address']
            )

        return user