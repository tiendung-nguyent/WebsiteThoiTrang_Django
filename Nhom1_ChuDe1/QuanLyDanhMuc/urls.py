from django.urls import path
from . import views

urlpatterns = [
    path('staff/QuanLyDanhMuc/', views.danh_muc_view, name='quanLyDM'),
]
