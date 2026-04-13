from django.apps import AppConfig


class QuanlynhaphangConfig(AppConfig):
    name = 'QuanLyNhapHang'

    def ready(self):
        import QuanLyNhapHang.signals

