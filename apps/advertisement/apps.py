from django.apps import AppConfig


class AdvertisementAppDefaultConfig(AppConfig):
    """Default configuration for Advertisement app
    """

    name = 'apps.advertisement'
    verbose_name = 'Advertisement'

    def ready(self):
        pass
