from django.apps import AppConfig


class DondatConfig(AppConfig):
    name = 'donDat'

    def ready(self):
        import donDat.signals
