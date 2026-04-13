from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Nhập mật khẩu (8-12 ký tự)'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Nhập lại mật khẩu'}))
    
    gender = forms.ChoiceField(choices=Profile.GENDER_CHOICES, widget=forms.RadioSelect)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': '0123456789'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': '0123456789'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@gmail.com'}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                gender=self.cleaned_data['gender'],
                birth_date=self.cleaned_data['birth_date'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user
