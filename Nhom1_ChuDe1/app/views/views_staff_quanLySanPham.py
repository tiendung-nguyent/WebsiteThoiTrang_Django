from django.shortcuts import render

def quanLySP(request):
    return render(request, 'staff/quanLySanPham/quanLySanPham.html')
def add_quanLySP(request):

    return render(request, 'staff/quanLySanPham/add_quanLySanPham.html')
def view_quanLySP(request):
    return render(request, 'staff/quanLySanPham/view_quanLySanPham.html')
def edit_quanLySP(request):
    return render(request, 'staff/quanLySanPham/edit_quanLySanPham.html')
def delete_quanLySP(request):
    return render(request, 'staff/quanLySanPham/delete_quanLySanPham.html')