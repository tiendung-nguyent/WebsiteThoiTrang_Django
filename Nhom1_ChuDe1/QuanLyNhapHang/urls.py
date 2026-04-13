from django.urls import path
from . import views

urlpatterns = [
    path('quan-ly-nhap-hang/', views.nhap_hang_view, name='quan_ly_nhap_hang'),
    path('quan-ly-nhap-hang/tao-don-nhap/', views.add_nhap_hang, name='tao_don_nhap'),
    path('quan-ly-nhap-hang/get-variants/', views.get_variants, name='get_variants'),
    path('quan-ly-nhap-hang/xoa-don-nhap/<str:ma_dn>/', views.delete_nhap_hang, name='xoa_don_nhap'),
    path('quan-ly-nhap-hang/chi-tiet-don-nhap/<str:ma_dn>/', views.get_detail_nhap_hang, name='chi_tiet_don_nhap'),
]