from django.db import models
from QuanLyDanhMuc.models import DanhMuc

class SanPham(models.Model):
    TRANG_THAI_CHOICES = [
        (0, 'Đang bán'),
        (1, 'Hết hàng'),
        (2, 'Ngừng bán'),
    ]

    SP_Ma = models.CharField(max_length=10, primary_key=True)

    def save(self, *args, **kwargs):
        if not self.SP_Ma:
            last_sp = SanPham.objects.all().order_by('SP_Ma').last()
            if not last_sp:
                self.SP_Ma = 'SP0000001'
            else:
                last_number = int(last_sp.SP_Ma[2:])
                new_number = last_number + 1
                self.SP_Ma = 'SP' + str(new_number).zfill(7)

        super(SanPham, self).save(*args, **kwargs)
    DM_Ma = models.ForeignKey(DanhMuc, on_delete=models.CASCADE, related_name='san_pham_thuoc_dm')
    SP_Ten = models.CharField(max_length=100)
    SP_GiaBan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    SP_MoTa = models.TextField(null=True, blank=True)
    SP_HinhAnh = models.ImageField(upload_to="sanpham/", null=True, blank=True)
    SP_TrangThai = models.IntegerField(
        choices=TRANG_THAI_CHOICES,
        default=0
    )

    def __str__(self):
        return self.SP_Ten

class BienTheSanPham(models.Model):
    BTSP_Ma = models.CharField(max_length=9, primary_key=True)
    def save(self, *args, **kwargs):
        if not self.BTSP_Ma:
            last_bt = BienTheSanPham.objects.all().order_by('BTSP_Ma').last()
            if not last_bt:
                self.BTSP_Ma = 'BT0000001'
            else:
                last_number = int(last_bt.BTSP_Ma[2:])
                new_number = last_number + 1
                self.BTSP_Ma = 'BT' + str(new_number).zfill(7)

        super(BienTheSanPham, self).save(*args, **kwargs)
    SP_Ma = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    SP_SL = models.IntegerField(default=0)
    SP_KichThuoc = models.CharField(max_length=5)
    SP_MauSac = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.BTSP_Ma} - {self.SP_KichThuoc} - {self.SP_MauSac}"
