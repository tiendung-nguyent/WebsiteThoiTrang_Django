from django.db import models

class NhaCungCap(models.Model):
    NCC_Ma = models.CharField(max_length=9, primary_key=True)
    NCC_Ten = models.CharField(max_length=100)
    NCC_SDT = models.CharField(max_length=10)
    NCC_DChi = models.TextField()

    def __str__(self):
        return self.NCC_Ten
