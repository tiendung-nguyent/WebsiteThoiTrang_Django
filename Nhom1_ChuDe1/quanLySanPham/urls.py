from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('staff/quanLySanPham/', views.quanLySP, name='quanLySP'),
    path('staff/quanLySanPham/add/', views.add_quanLySP, name='add_quanLySP'),
    path('staff/quanLySanPham/view/<str:ma_sp>/', views.view_quanLySP, name='view_quanLySP'),
    path('staff/quanLySanPham/edit/', views.edit_quanLySP, name='edit_quanLySP'),
    path('staff/quanLySanPham/delete/<str:ma_sp>/', views.delete_quanLySP, name='delete_quanLySP'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
