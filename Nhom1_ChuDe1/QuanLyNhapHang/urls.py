from django.urls import path
from . import views

urlpatterns = [
    path('staff/quan-ly-nhap-hang/', views.nhap_hang_view, name='quan_ly_nhap_hang'),
]
