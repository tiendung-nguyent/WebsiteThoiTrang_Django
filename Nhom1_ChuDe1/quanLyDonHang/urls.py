from django.urls import path
from . import views

urlpatterns = [
    path('staff/quanLyDonHang/', views.quanLyDonHang, name='quanLyDonHang'),
    path('staff/quanLyDonHang/view/<str:status>/', views.view_quanLyDonHang, name='view_quanLyDonHang'),
]
