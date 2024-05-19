from django.apps import AppConfig


class kahamahmisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kahamahmis'
    
    def ready(self):
        import kahamahmis.signals
