from random import randint

from django.core.management.base import BaseCommand

from apps.advertisement.factories import (
    AdvertisementFactory,
    CommentFactory,
    ComplaintFactory,
    ImageFactory,
)


class Command(BaseCommand):
    """The command to generate adverts"""

    help = "Generates a specific amount of adverts"

    def add_arguments(self, parser):
        parser.add_argument(
            'amount',
            type=int,
            help='an amount of adverts'
        )
        parser.add_argument(
            '--comments',
            action='store_true',
            help='add comments to adverts'
        )
        parser.add_argument(
            '--complaints',
            action='store_true',
            help='add complaints to adverts'
        )

    def handle(self, *args, **options):
        """The function that handles the user's input"""
        amount = options['amount']
        create_comment = options.get('comments', False)
        create_complaint = options.get('complaints', False)
        for _ in range(amount):
            advert = AdvertisementFactory()
            for _ in range(randint(1, 5)):
                ImageFactory(advertisement=advert)
            if create_comment:
                CommentFactory(advertisement=advert)
            if create_complaint:
                ComplaintFactory(advertisement=advert)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {amount} adverts')
        )
