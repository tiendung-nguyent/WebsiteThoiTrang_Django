from django.urls import path
from . import views

urlpatterns = [
    path('staff/khuyen-mai/', views.quan_ly_khuyen_mai_view, name='quan_ly_khuyen_mai'),
]
