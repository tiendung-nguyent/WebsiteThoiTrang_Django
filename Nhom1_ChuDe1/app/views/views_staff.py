from django.shortcuts import render

def bao_cao_view(request):
    return render(request, 'staff/BaoCaoThongKe/BaoCaoThongKe.html')