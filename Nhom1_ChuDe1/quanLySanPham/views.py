from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SanPhamForm

def quanLySP(request):
    return render(request, 'quanLySanPham/quanLySanPham.html')

def add_quanLySP(request):
    if request.method == 'POST':
        form = SanPhamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lưu sản phẩm thành công!')
            return redirect('quanLySP')
    else:
        form = SanPhamForm()
    return render(request, 'quanLySanPham/add_quanLySanPham.html', {'form': form})

def view_quanLySP(request):
    return render(request, 'quanLySanPham/view_quanLySanPham.html')
def edit_quanLySP(request):
    return render(request, 'quanLySanPham/edit_quanLySanPham.html')
def delete_quanLySP(request):
    return render(request, 'quanLySanPham/delete_quanLySanPham.html')
