from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    verbose_name = 'Auto Parts Inventory'
    
    def ready(self):
        import myapp.signals
        print("✅ Signals loaded successfully!")