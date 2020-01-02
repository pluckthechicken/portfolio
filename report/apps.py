from django.apps import AppConfig

class ReportConfig(AppConfig):
    name = 'report'
    verbose_name = 'Portfolio report'
    def ready(self):
        pass
