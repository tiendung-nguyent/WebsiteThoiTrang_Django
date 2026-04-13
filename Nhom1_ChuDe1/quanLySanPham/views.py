from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SanPhamForm
from .models import SanPham


def quanLySP(request):
    return render(request, 'quanLySanPham/quanLySanPham.html')


def get_next_sp_ma():
    last_sp = SanPham.objects.all().order_by('SP_Ma').last()

    if not last_sp:
        return "SP0000001"

    try:
        last_ma = last_sp.SP_Ma
        number_part = int(last_ma[2:])

        new_number = number_part + 1

        return f"SP{new_number:07d}"

    except (ValueError, IndexError):
        # Phòng trường hợp mã cũ bị lỗi định dạng
        return "SP0000001"


def add_quanLySP(request):
    if request.method == 'POST':
        form = SanPhamForm(request.POST)
        if form.is_valid():

            form.save()
            messages.success(request, 'Lưu sản phẩm thành công!')
            return redirect('quanLySP')
    else:
        form = SanPhamForm()


    next_ma = get_next_sp_ma()
    return render(request, 'quanLySanPham/add_quanLySanPham.html', {
        'form': form,
        'next_ma': next_ma
    })
def    view_quanLySP(request):
    return render(request, 'quanLySanPham/view_quanLySanPham.html')
def edit_quanLySP(request):
    return render(request, 'quanLySanPham/edit_quanLySanPham.html')
def delete_quanLySP(request):
    return render(request, 'quanLySanPham/delete_quanLySanPham.html')
