from django.urls import path
from . import views

urlpatterns = [
    path('staff/nha-cung-cap/', views.quan_ly_ncc_view, name='quan_ly_ncc'),
    path('staff/nha-cung-cap/them/', views.them_ncc_view, name='them_ncc'),
    path('staff/nha-cung-cap/sua/<str:ma_ncc>/', views.sua_ncc_view, name='sua_ncc'),
    path('staff/nha-cung-cap/xoa/<str:ma_ncc>/', views.xoa_ncc_view, name='xoa_ncc'),
]
