from django.urls import path
from . import views

urlpatterns = [
    path('staff/QuanLyKhachHang/', views.khach_hang_view, name='quanLyKH'),
]
