from django.urls import path
from . import views

urlpatterns = [
    path('quan-ly-don-hang-user/', views.quanLyDonDat, name='quanLyDonDat'),
]
