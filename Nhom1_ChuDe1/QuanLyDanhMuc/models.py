from django.db import models

class DanhMuc(models.Model):
    DM_Ma = models.CharField(max_length=9, primary_key=True)
    DM_Ten = models.CharField(max_length=100)
    DM_Thuoc = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.DM_Ten
