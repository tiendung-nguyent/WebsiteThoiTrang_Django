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
        status_map = {
            'đang bán': 0,
            'hết hàng': 1,
            'ngừng bán': 2
        }
        
        q_obj = Q(SP_Ma__icontains=query) | Q(SP_Ten__icontains=query)
        
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
        return "SP0000001"


@user_passes_test(lambda u: u.is_staff)
def add_quanLySP(request):
    if request.method == 'POST':
        form = SanPhamForm(request.POST, request.FILES)
        if form.is_valid():
            new_sp = form.save()

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

    variants = BienTheSanPham.objects.filter(SP_Ma=sp)
    sizes = sorted(variants.values_list('SP_KichThuoc', flat=True).distinct())
    colors = sorted(variants.values_list('SP_MauSac', flat=True).distinct())

    sizes_str = ", ".join(sizes) if sizes else "Không có"
    colors_str = ", ".join(colors) if colors else "Không có"

    if request.user.is_authenticated:
        viewed_products = request.session.get('viewed_products', [])
        current_product = [sp.SP_Ma, sp.SP_Ten]

        if current_product in viewed_products:
            viewed_products.remove(current_product)

        viewed_products.insert(0, current_product)

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

            # Đồng bộ các biến thể thay vì xóa hết tạo lại (để tránh mất lịch sử nhập hàng và các ràng buộc FK)
            sizes = request.POST.getlist('bienthe_size[]')
            colors = request.POST.getlist('bienthe_color[]')
            quantities = request.POST.getlist('bienthe_soluong[]')

            # Lấy danh sách các biến thể hiện tại
            current_variants = BienTheSanPham.objects.filter(SP_Ma=updated_sp)
            variant_map = {(v.SP_KichThuoc, v.SP_MauSac): v for v in current_variants}
            processed_keys = set()

            if sizes and colors and quantities:
                for i in range(len(sizes)):
                    size = sizes[i]
                    color = colors[i]
                    key = (size, color)
                    try:
                        qty = int(quantities[i])
                        if qty < 0: qty = 0
                    except ValueError:
                        qty = 0
                    
                    if key in variant_map:
                        # Cập nhật biến thể hiện có
                        btsp = variant_map[key]
                        btsp.SP_SL = qty
                        btsp.save()
                    else:
                        # Tạo biến thể mới
                        BienTheSanPham.objects.create(
                            SP_Ma=updated_sp,
                            SP_KichThuoc=size,
                            SP_MauSac=color,
                            SP_SL=qty
                        )
                    processed_keys.add(key)

            # Xóa các biến thể không còn trong danh sách mới (nếu không có ràng buộc quan trọng)
            for key, btsp in variant_map.items():
                if key not in processed_keys:
                    # Trước khi xóa, kiểm tra xem có dữ liệu liên quan không
                    # Nếu có ChiTietNhapHang hoặc tương tự, có thể nên báo lỗi hoặc đổi trạng thái
                    # Ở đây tạm thời cho phép xóa để giữ tính năng cũ nhưng an toàn hơn
                    btsp.delete()

            messages.success(request, f'Cập nhật sản phẩm {ma_sp} thành công!')
            return redirect('quanLySP')
    else:
        form = SanPhamForm(instance=sp)

    existing_sizes = list(variants.values_list('SP_KichThuoc', flat=True).distinct())
    existing_colors = list(variants.values_list('SP_MauSac', flat=True).distinct())

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