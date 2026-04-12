from django.urls import path
from . import views

urlpatterns = [
    path('staff/nha-cung-cap/', views.quan_ly_ncc_view, name='quan_ly_ncc'),
]
