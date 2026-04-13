from django.urls import path
from . import views

urlpatterns = [
    path('staff/khuyen-mai/', views.quan_ly_khuyen_mai_view, name='quan_ly_khuyen_mai'),
    path('staff/khuyen-mai/them/', views.them_khuyen_mai_view, name='them_khuyen_mai'),
    path('staff/khuyen-mai/sua/<str:ma_km>/', views.sua_khuyen_mai_view, name='sua_khuyen_mai'),
    path('staff/khuyen-mai/xoa/<str:ma_km>/', views.xoa_khuyen_mai_view, name='xoa_khuyen_mai'),
]
