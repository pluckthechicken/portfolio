from django.apps import AppConfig
from .views import plot_history

class ReportConfig(AppConfig):
    name = 'report'
    verbose_name = 'Portfolio report'
    def ready(self):
        plot_history()
