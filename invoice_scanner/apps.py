from django.apps import AppConfig

class InvoiceScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoice_scanner'

    def ready(self):
        import invoice_scanner.signals