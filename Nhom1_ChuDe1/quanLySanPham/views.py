import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from .forms import SanPhamForm
from .models import SanPham, BienTheSanPham


@user_passes_test(lambda u: u.is_staff)
def quanLySP(request):
    query = request.GET.get('q', '')
    products = SanPham.objects.all().order_by('-SP_Ma')

    if query:
        # Mapping status strings to integers
        status_map = {
            'đang bán': 0,
            'hết hàng': 1,
            'ngừng bán': 2
        }
        
        q_obj = Q(SP_Ma__icontains=query) | Q(SP_Ten__icontains=query)
        
        # Check if query matches a status
        if query.lower() in status_map:
            q_obj |= Q(SP_TrangThai=status_map[query.lower()])
            
        products = products.filter(q_obj)

    return render(request, 'quanLySanPham/quanLySanPham.html', {
        'products': products,
        'query': query
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


@user_passes_test(lambda u: u.is_staff)
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

    # Store recently viewed products in session
    if request.user.is_authenticated:
        viewed_products = request.session.get('viewed_products', [])
        current_product = [sp.SP_Ma, sp.SP_Ten]

        # Remove if already exists to move to top
        if current_product in viewed_products:
            viewed_products.remove(current_product)

        # Insert at top
        viewed_products.insert(0, current_product)

        # Limit to 10
        request.session['viewed_products'] = viewed_products[:10]
        request.session.modified = True

    return render(request, 'quanLySanPham/view_quanLySanPham.html', {
        'sp': sp,
        'sizes_str': sizes_str,
        'colors_str': colors_str
    })


@user_passes_test(lambda u: u.is_staff)
def edit_quanLySP(request, ma_sp):
    sp = get_object_or_404(SanPham, SP_Ma=ma_sp)
    variants = BienTheSanPham.objects.filter(SP_Ma=sp)

    if request.method == 'POST':
        form = SanPhamForm(request.POST, request.FILES, instance=sp)
        if form.is_valid():
            updated_sp = form.save()

            # Xử lý biến thể: Xóa các biến thể cũ và tạo mới để đồng bộ
            # (Hoặc có thể cập nhật, nhưng xóa/tạo mới đơn giản hơn cho logic này)
            BienTheSanPham.objects.filter(SP_Ma=updated_sp).delete()

            sizes = request.POST.getlist('bienthe_size[]')
            colors = request.POST.getlist('bienthe_color[]')
            quantities = request.POST.getlist('bienthe_soluong[]')

            if sizes and colors and quantities:
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

    # Lấy danh sách kích thước và màu sắc hiện tại để pre-activate tags trong template
    existing_sizes = list(variants.values_list('SP_KichThuoc', flat=True).distinct())
    existing_colors = list(variants.values_list('SP_MauSac', flat=True).distinct())

    # Tạo mapping để pre-fill số lượng trong bảng biến thể
    variant_data = []
    for v in variants:
        variant_data.append({
            'size': v.SP_KichThuoc,
            'color': v.SP_MauSac,
            'qty': v.SP_SL
        })

    return render(request, 'quanLySanPham/edit_quanLySanPham.html', {
        'form': form,
        'sp': sp,
        'existing_sizes': existing_sizes,
        'existing_colors': existing_colors,
        'variant_data': variant_data,
        'default_sizes': ['S', 'M', 'L', 'XL', 'XXL'],
        'default_colors': ['Đen', 'Trắng', 'Xanh', 'Đỏ', 'Xám', 'Vàng']
    })


@user_passes_test(lambda u: u.is_staff)
def delete_quanLySP(request, ma_sp):
    sp = get_object_or_404(SanPham, SP_Ma=ma_sp)

    if request.method == 'POST':
        sp.delete()
        messages.success(request, f'Xóa sản phẩm {ma_sp} thành công!')
        return redirect('quanLySP')

    return render(request, 'quanLySanPham/delete_quanLySanPham.html', {'sp': sp})