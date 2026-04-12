from django.urls import path
from . import views

urlpatterns = [
    path('staff/quanLySanPham/', views.quanLySP, name='quanLySP'),
    path('staff/quanLySanPham/add/', views.add_quanLySP, name='add_quanLySP'),
    path('staff/quanLySanPham/view/', views.view_quanLySP, name='view_quanLySP'),
    path('staff/quanLySanPham/edit/', views.edit_quanLySP, name='edit_quanLySP'),
    path('staff/quanLySanPham/delete/', views.delete_quanLySP, name='delete_quanLySP'),

]
