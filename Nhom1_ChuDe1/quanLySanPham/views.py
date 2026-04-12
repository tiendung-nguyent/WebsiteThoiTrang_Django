from django.shortcuts import render
def quanLySP(request):
    return render(request, 'quanLySanPham/quanLySanPham.html')
def add_quanLySP(request):
    return render(request, 'quanLySanPham/add_quanLySanPham.html')
def view_quanLySP(request):
    return render(request, 'quanLySanPham/view_quanLySanPham.html')
def edit_quanLySP(request):
    return render(request, 'quanLySanPham/edit_quanLySanPham.html')
def delete_quanLySP(request):
    return render(request, 'quanLySanPham/delete_quanLySanPham.html')
