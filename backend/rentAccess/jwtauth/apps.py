from django.apps import AppConfig


class JwtauthConfig(AppConfig):
    name = 'jwtauth'

    def ready(self):
        import jwtauth.signals
