from django.core.management import BaseCommand, CommandError

from factory import errors as factory_errors


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ Command handler """

        result = self.generate_user_rows(options['amount'])

        if result:
            print('Successful')
        else:
            raise CommandError('Something went wrong. Check DB')

    def add_arguments(self, parser):
        """ Arguments parser """
        # Specifying that amount is positional and always required
        parser.add_argument(
            'amount',
            type=self.check_5000,
            help='Enter how much rows you want to generate '
                 '(Limit is 5000 rows in 1 execution)'
        )

    @staticmethod
    def generate_user_rows(number):
        from apps.users.factories import SocialAuthUserFactory
        try:
            for _ in range(number):
                SocialAuthUserFactory()
            return True
        except (
            factory_errors.FactoryError,
            factory_errors.AssociatedClassError,
            AttributeError
        ):
            return False

    @staticmethod
    def check_5000(value):
        value = int(value)
        if value > 5000:
            raise SystemExit('Error: You can create 5000 rows at once')

        return value
