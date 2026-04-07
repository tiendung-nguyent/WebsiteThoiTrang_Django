# Create your models here.
from django.db import models


class KhachHang(models.Model):
    KH_Ma = models.CharField(max_length=9, primary_key=True)
    KH_Ten = models.CharField(max_length=100)
    KH_TongChiTieu = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    KH_SoDonHang = models.IntegerField(default=0)

    def __str__(self):
        return self.KH_Ten


class ChiTietKhachHang(models.Model):
    CTKH_Ma = models.CharField(max_length=9, primary_key=True)
    KH_Ma = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    CTKH_HoTenNguoiNhan = models.CharField(max_length=100)
    CTKH_SDT = models.CharField(max_length=10)
    CTKH_DiaChi = models.TextField()

    def __str__(self):
        return f"{self.CTKH_HoTenNguoiNhan} - {self.CTKH_Ma}"


class GioHang(models.Model):
    GH_Ma = models.CharField(max_length=9, primary_key=True)
    KH_Ma = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    GH_TongSL = models.IntegerField(default=0)
    GH_TamTinh = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.GH_Ma


class DonDat(models.Model):
    TT_Ma = models.CharField(max_length=9, primary_key=True)  # Mã thanh toán/đơn hàng
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

    def __str__(self):
        return f"{self.SP_Ma.SP_Ten} trong giỏ {self.GH_Ma.GH_Ma} (SL: {self.GH_SL})"

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

    def __str__(self):
        return f"{self.SP_Ma.SP_Ten} - KM: {self.KM_Ma.KM_Ten}"


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

    def __str__(self):
        return self.NH_Ma

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
