# bước 1.
from django import forms
from ..models import NhapHang, NhaCungCap


class NhapHangForm(forms.ModelForm):
    class Meta:
        model = NhapHang
        # Các trường này phải khớp chính xác với tên biến trong models.py của bạn
        fields = ['NH_Ma', 'NCC_Ma', 'NH_TongTien']

        # Thêm các class CSS để giao diện đồng nhất với phong cách của bạn
        widgets = {
            'NH_Ma': forms.TextInput(attrs={'placeholder': 'Mã đơn (ví dụ: NH001)'}),
            'NCC_Ma': forms.Select(),
            'NH_TongTien': forms.NumberInput(attrs={'value': 0}),
        }