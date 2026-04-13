from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register_success')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def register_success(request):
    return render(request, 'registration/register_success.html')

@login_required
def profile(request):
    # 'viewed_products' will be populated in quanLySanPham views
    viewed_products = request.session.get('viewed_products', [])
    return render(request, 'user/profile.html', {
        'user': request.user,
        'viewed_products': viewed_products
    })

def logout_view(request):
    logout(request)
    return redirect('trangChuUser')
