# Create your models here.
from django.db import models


class KhachHang(models.Model):
    KH_Ma = models.CharField(max_length=9, primary_key=True)
    KH_Ten = models.CharField(max_length=100)
    KH_SDT = models.CharField(max_length=10)
    KH_DiaChi = models.TextField()
    KH_TongChiTieu = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    KH_SoDonHang = models.IntegerField(default=0)

    def __str__(self):
        return self.KH_Ten


class GioHang(models.Model):
    GH_Ma = models.CharField(max_length=9, primary_key=True)
    GH_TamTinh = models.DecimalField(max_digits=10, decimal_places=2)
    GH_TongSL = models.IntegerField()

    def __str__(self):
        return self.GH_Ma


# 3. Bảng Thanh toán
class ThanhToan(models.Model):
    TT_Ma = models.CharField(max_length=9, primary_key=True)
    GH_Ma = models.ForeignKey(GioHang, on_delete=models.CASCADE)
    TT_HoTen = models.CharField(max_length=100)
    TT_SDT = models.CharField(max_length=10)
    TT_DiaChi = models.TextField()
    TT_PhuongThuc = models.CharField(max_length=50)
    TT_TongTienHang = models.DecimalField(max_digits=10, decimal_places=2)
    TT_TongPhiVC = models.DecimalField(max_digits=10, decimal_places=2)
    TT_TongThanhToan = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.TT_Ma} - {self.TT_HoTen}"

class DatHang(models.Model):
    DH_Ma = models.CharField(max_length=9, primary_key=True)
    TT_Ma = models.ForeignKey(ThanhToan, on_delete=models.PROTECT)
    KH_Ma = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    DH_Ngay = models.DateField(auto_now_add=True)
    DH_TongSL = models.IntegerField()
    DH_TrangThai = models.CharField(max_length=50)

    def __str__(self):
        return f"Đơn {self.DH_Ma} ({self.DH_Ngay.strftime('%d/%m/%Y')})"

class DonHangVanChuyen(models.Model):
    DH_MaVanChuyen = models.CharField(max_length=9, primary_key=True)
    DH_Ma = models.OneToOneField(DatHang, on_delete=models.CASCADE)
    DH_DViVanChuyen = models.CharField(max_length=100)
    DH_PhiCuoc = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.DH_DViVanChuyen

class DanhMuc(models.Model):
    DM_Ma = models.CharField(max_length=9, primary_key=True)
    DM_Ten = models.CharField(max_length=100)
    DM_Thuoc = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.DM_Ten



class SanPham(models.Model):
    SP_Ma = models.CharField(max_length=10, primary_key=True)
    DM_Ma = models.ForeignKey(DanhMuc, on_delete=models.CASCADE, related_name='san_pham_thuoc_dm')
    SP_Ten = models.CharField(max_length=100)
    SP_GiaBan = models.DecimalField(max_digits=10, decimal_places=2)
    SP_MoTa = models.TextField(null=True, blank=True)
    SP_URLHinhAnh = models.URLField(max_length=500, null=True, blank=True)
    SP_TrangThai = models.CharField(max_length=50)

    def __str__(self):
        return self.SP_Ten


class ChiTietGioHang(models.Model):
    GH_Ma = models.ForeignKey(GioHang, on_delete=models.CASCADE)
    SP_Ma = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    GH_SL = models.IntegerField(default=1)
    GH_TTien = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (('GH_Ma', 'SP_Ma'),)




class KhuyenMai(models.Model):
    KM_Ma = models.CharField(max_length=9, primary_key=True)
    KM_GiaTri = models.DecimalField(max_digits=10, decimal_places=2)
    KM_NgayBD = models.DateField()
    KM_NgayKT = models.DateField()
    KM_Ten = models.CharField(max_length=100)
    KM_Loai = models.CharField(max_length=50)

    def __str__(self):
        return self.KM_Ten


class SanPham_KhuyenMai(models.Model):
    SP_Ma = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    KM_Ma = models.ForeignKey(KhuyenMai, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('SP_Ma', 'KM_Ma'),)


class NhaCungCap(models.Model):
    NCC_Ma = models.CharField(max_length=9, primary_key=True)
    NCC_Ten = models.CharField(max_length=100)
    NCC_SDT = models.CharField(max_length=10)
    NCC_DChi = models.TextField()

    def __str__(self):
        return self.NCC_Ten


class NhapHang(models.Model):
    NH_Ma = models.CharField(max_length=9, primary_key=True)
    NCC_Ma = models.ForeignKey(NhaCungCap, on_delete=models.CASCADE)
    NH_Ngay = models.DateField(auto_now_add=True)
    NH_TongTien = models.DecimalField(max_digits=10, decimal_places=2)


class BienTheSanPham(models.Model):
    BTSP_Ma = models.CharField(max_length=9, primary_key=True)
    SP_Ma = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    SP_SL = models.IntegerField(default=0)
    SP_KichThuoc = models.CharField(max_length=5)
    SP_MauSac = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.BTSP_Ma} - {self.SP_KichThuoc} - {self.SP_MauSac}"


class ChiTietNhapHang(models.Model):
    BTSP_Ma = models.ForeignKey(BienTheSanPham, on_delete=models.CASCADE)
    NH_Ma = models.ForeignKey(NhapHang, on_delete=models.CASCADE)
    NH_DonGia = models.DecimalField(max_digits=10, decimal_places=2)
    NH_SL = models.IntegerField()
    NH_TTien = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (('BTSP_Ma', 'NH_Ma'),)