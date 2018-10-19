from django.conf import settings
from django.core.management import BaseCommand

from oauth2_provider.models import Application


class DBError(Exception):
    """ If anything went wrong with DB driver, throw an exception"""
    pass


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ Command handler """

        try:
            self.generate_apps()
        except DBError:
            # Reset state to the default one
            Application.objects.all().delete()
            raise DBError

        print('Successful')

    @staticmethod
    def generate_apps():
        """ Listcomp for the App creation """
        [
            Application.objects.create(
                name=f'{match}_app',
                user=None,
                client_type="confidential",
                authorization_grant_type="password",
            ).save()
            for match in settings.LOCAL_SOCIAL_AUTH_APP_BACKENDS if
            not Application.objects.filter(name=f'{match}_app').exists()
        ]
