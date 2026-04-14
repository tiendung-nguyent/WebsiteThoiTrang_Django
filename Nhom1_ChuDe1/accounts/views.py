from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import Profile


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
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    return render(request, 'user/profile.html', {
        'user': request.user,
        'profile': profile_obj,
        'viewed_products': viewed_products
    })


def logout_view(request):
    logout(request)
    return redirect('trangChuUser')