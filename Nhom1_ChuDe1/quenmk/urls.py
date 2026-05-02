from django.urls import path
from . import views

urlpatterns = [
    path('nhap-sdt/', views.nhap_sdt, name='nhap_sdt'),
    path('nhap-otp/', views.nhap_otp, name='nhap_otp'),
    path('tao-mk-moi/', views.tao_mk_moi, name='tao_mk_moi'),
    path('thanh-cong/', views.thanh_cong, name='thanh_cong'),
]
