import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SanPhamForm
from .models import SanPham, BienTheSanPham

def quanLySP(request):
    products = SanPham.objects.all().order_by('-SP_Ma')

    return render(request, 'quanLySanPham/quanLySanPham.html', {
        'products': products
    })

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
        form = SanPhamForm(request.POST, request.FILES)
        if form.is_valid():
            new_sp = form.save()
            
            # Lấy dữ liệu mảng các biến thể từ Form UI HTML
            sizes = request.POST.getlist('bienthe_size[]')
            colors = request.POST.getlist('bienthe_color[]')
            quantities = request.POST.getlist('bienthe_soluong[]')
            
            if sizes and colors and quantities:
                for i in range(len(sizes)):
                    try:
                        qty = int(quantities[i])
                        if qty >= 0:
                            BienTheSanPham.objects.create(
                                SP_Ma=new_sp,
                                SP_KichThuoc=sizes[i],
                                SP_MauSac=colors[i],
                                SP_SL=qty
                            )
                    except ValueError:
                        pass

            messages.success(request, 'Lưu sản phẩm thành công!')
            return redirect('quanLySP')
    else:
        form = SanPhamForm()


    next_ma = get_next_sp_ma()
    return render(request, 'quanLySanPham/add_quanLySanPham.html', {
        'form': form,
        'next_ma': next_ma
    })
def view_quanLySP(request, ma_sp):
    sp = get_object_or_404(SanPham, SP_Ma=ma_sp)
    
    # Query distinct sizes and colors from associated BienTheSanPham
    variants = BienTheSanPham.objects.filter(SP_Ma=sp)
    sizes = sorted(variants.values_list('SP_KichThuoc', flat=True).distinct())
    colors = sorted(variants.values_list('SP_MauSac', flat=True).distinct())
    
    sizes_str = ", ".join(sizes) if sizes else "Không có"
    colors_str = ", ".join(colors) if colors else "Không có"
    
    return render(request, 'quanLySanPham/view_quanLySanPham.html', {
        'sp': sp,
        'sizes_str': sizes_str,
        'colors_str': colors_str
    })
def edit_quanLySP(request, ma_sp):
    sp = get_object_or_404(SanPham, SP_Ma=ma_sp)
    
    if request.method == 'POST':
        form = SanPhamForm(request.POST, request.FILES, instance=sp)
        if form.is_valid():
            updated_sp = form.save()
            
            # Xử lý biến thể: Xóa cũ, thêm mới (theo logic tương tự add)
            sizes = request.POST.getlist('bienthe_size[]')
            colors = request.POST.getlist('bienthe_color[]')
            quantities = request.POST.getlist('bienthe_soluong[]')
            
            if sizes and colors and quantities:
                # Xóa các biến thể hiện tại để cập nhật mới
                BienTheSanPham.objects.filter(SP_Ma=updated_sp).delete()
                
                for i in range(len(sizes)):
                    try:
                        qty = int(quantities[i])
                        if qty >= 0:
                            BienTheSanPham.objects.create(
                                SP_Ma=updated_sp,
                                SP_KichThuoc=sizes[i],
                                SP_MauSac=colors[i],
                                SP_SL=qty
                            )
                    except ValueError:
                        pass
            
            messages.success(request, f'Cập nhật sản phẩm {ma_sp} thành công!')
            return redirect('quanLySP')
    else:
        form = SanPhamForm(instance=sp)

    # Lấy danh sách biến thể hiện có để hiển thị trên UI
    existing_variants = BienTheSanPham.objects.filter(SP_Ma=sp)
    
    return render(request, 'quanLySanPham/edit_quanLySanPham.html', {
        'form': form,
        'sp': sp,
        'existing_variants': existing_variants
    })
def delete_quanLySP(request):
    return render(request, 'quanLySanPham/delete_quanLySanPham.html')
