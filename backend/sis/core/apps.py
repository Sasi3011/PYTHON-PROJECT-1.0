from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sis.core'
    
    def ready(self):
        # Import and run the populate_default_data function when Django starts
        # Commented out until MongoDB is configured
        # from .utils.crop_database import populate_default_data
        # populate_default_data()
        pass
