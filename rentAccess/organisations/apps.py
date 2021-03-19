from django.apps import AppConfig


class OrganisationsConfig(AppConfig):
    name = 'organisations'

    def ready(self):
        """Initializes signals.
        """
        from . import signals
        return True
