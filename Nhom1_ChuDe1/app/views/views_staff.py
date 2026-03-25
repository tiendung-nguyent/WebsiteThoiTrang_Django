from django.shortcuts import render

def bao_cao_view(request):
    return render(request, 'staff/bao_cao.html')