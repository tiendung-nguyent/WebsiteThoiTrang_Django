from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def quanLyDonDat(request):
    return render(request, 'donDat/quanLyDonDat.html')
