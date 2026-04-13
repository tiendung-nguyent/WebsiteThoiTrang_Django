from django.db import models
from donDat.models import DonDat

class DonHangVanChuyen(models.Model):
    DH_MaVanChuyen = models.CharField(max_length=9, primary_key=True)
    TT_Ma = models.ForeignKey(DonDat, on_delete=models.CASCADE)
    DH_DViVanChuyen = models.CharField(max_length=200)
    DH_PhiCuoc = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.DH_MaVanChuyen
