from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied

class StaffAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/staff/'):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.path}")
            if not request.user.is_staff and not request.user.is_superuser:
                raise PermissionDenied("Chỉ quản trị viên mới được phép truy cập trang này.")
                
        response = self.get_response(request)
        return response
