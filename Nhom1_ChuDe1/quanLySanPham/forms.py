from django import forms
from .models import SanPham

class SanPhamForm(forms.ModelForm):
    class Meta:
        model = SanPham
        fields = ['SP_Ten', 'DM_Ma', 'SP_GiaBan', 'SP_HinhAnh', 'SP_MoTa', 'SP_TrangThai']
        widgets = {
            'SP_Ten': forms.TextInput(attrs={'placeholder': 'Nhập tên sản phẩm', 'required': True}),
            'DM_Ma': forms.Select(attrs={'required': True}),
            'SP_GiaBan': forms.NumberInput(attrs={'value': '0', 'required': True}),
            'SP_HinhAnh': forms.FileInput(attrs={'class': 'form-control-file'}),
            'SP_MoTa': forms.Textarea(attrs={'rows': 3}),
            'SP_TrangThai': forms.Select(attrs={'required': True}),
        }
