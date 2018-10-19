from django.test import TestCase

from apps.advertisement import models
from apps.advertisement.factories import (
    AdvertisementFactory,
    CommentFactory,
    ComplaintFactory,
    ImageFactory,
    UserFactory,
)
from apps.advertisement.views import AdvertisementPage


class AdvertTest(TestCase):
    """Check if adverts, comments and complaints actually get created"""

    def test_defining(self):
        self.user = UserFactory(is_staff=True)
        self.advert = AdvertisementFactory()
        self.comment = CommentFactory()
        self.complaint = ComplaintFactory()
        self.image = ImageFactory()

    def test_add_complaints(self):
        self.user = UserFactory()

        self.advert = AdvertisementFactory()

        AdvertisementPage.add_complaint(
            self.advert.id,
            self.user,
            'complaint'
        )

        self.assertEqual(
            models.Complaints.objects.get(advertisement=self.advert).text,
            'complaint'
        )

    def test_add_comments(self):
        self.user = UserFactory()

        self.advert = AdvertisementFactory()

        AdvertisementPage.add_comment(
            self.advert.id,
            self.user,
            'comment'
        )

        self.assertEqual(
            models.Comments.objects.get(advertisement=self.advert).text,
            'comment'
        )
