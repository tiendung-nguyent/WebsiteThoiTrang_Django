from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Lấy dữ liệu thêm từ form
            phone_number = form.cleaned_data.get('phone_number', '')
            full_name = form.cleaned_data.get('full_name', '')
            address = form.cleaned_data.get('address', '')

            # Tạo hoặc cập nhật profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = phone_number
            profile.full_name = full_name
            profile.address = address
            profile.save()

            return redirect('register_success')
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