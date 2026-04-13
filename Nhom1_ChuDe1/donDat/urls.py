from django.urls import path
from . import views

urlpatterns = [
    path('', views.quanLyDonDat, name='quanLyDonDat'),
    path('huy/<str:tt_ma>/', views.huyDonDat, name='huyDonDat'),
]