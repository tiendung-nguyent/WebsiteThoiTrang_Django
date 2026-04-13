from django.urls import path
from . import views

urlpatterns = [
    path('staff/', views.bao_cao_view, name='bao_cao_staff'),
]
