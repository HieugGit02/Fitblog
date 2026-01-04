from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = '🛍️ Products & Recommendations'
    
    def ready(self):
        """Register signals when app is ready"""
        import products.signals
