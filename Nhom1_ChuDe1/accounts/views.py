from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from quanLyKhachHang.models import KhachHang


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user)
            messages.success(request, "Đăng ký tài khoản thành công!")

            return redirect('profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def register_success(request):
    return render(request, 'registration/register_success.html')


@login_required
def profile(request):
    viewed_products = request.session.get('viewed_products', [])
    kh_ma = f"KH{request.user.id:07d}"
    khach_hang = KhachHang.objects.filter(KH_Ma=kh_ma).first()

    return render(request, 'user/profile.html', {
        'user': request.user,
        'khach_hang': khach_hang,
        'viewed_products': viewed_products
    })


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def login_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('bao_cao_staff')
    return redirect('profile')