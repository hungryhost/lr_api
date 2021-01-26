from django.apps import AppConfig


class RegistrylockConfig(AppConfig):
    name = 'register'

    def ready(self):
        """Initializes signals.
        """
        from . import signals
        return True
