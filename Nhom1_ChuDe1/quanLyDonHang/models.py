from django.db import models
from gioHang.models import GioHang
from quanLyKhachHang.models import ChiTietKhachHang

class DonDat(models.Model):
    TT_Ma = models.CharField(max_length=9, primary_key=True)
    GH_Ma = models.ForeignKey(GioHang, on_delete=models.PROTECT)
    CTKH_Ma = models.ForeignKey(ChiTietKhachHang, on_delete=models.PROTECT)
    TT_TongPhiVC = models.DecimalField(max_digits=10, decimal_places=2)
    TT_TongThanhToan = models.DecimalField(max_digits=10, decimal_places=2)
    DH_TrangThai = models.CharField(max_length=50)
    TT_PhuongThuc = models.CharField(max_length=100)
    TT_TongTienHang = models.DecimalField(max_digits=10, decimal_places=2)
    TT_NgayThanhToan = models.DateField(null=True, blank=True)
    TT_NgayDatHang = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Đơn {self.TT_Ma} - {self.DH_TrangThai}"

class DonHangVanChuyen(models.Model):
    DH_MaVanChuyen = models.CharField(max_length=9, primary_key=True)
    TT_Ma = models.ForeignKey(DonDat, on_delete=models.CASCADE)
    DH_DViVanChuyen = models.CharField(max_length=200)
    DH_PhiCuoc = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.DH_MaVanChuyen
