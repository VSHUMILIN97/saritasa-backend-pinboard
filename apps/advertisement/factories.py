from random import randint

import factory
import faker

from . import models
from ..users.factories import UserFactory

fake = faker.Faker()


class AdvertisementFactory(factory.DjangoModelFactory):
    """Factory fot the advertisement model"""

    class Meta:
        model = models.Advertisement

    user = factory.SubFactory(UserFactory)
    title = factory.lazy_attribute(lambda a: fake.name())
    description = factory.lazy_attribute(lambda a: fake.text())
    address = factory.lazy_attribute(lambda a: fake.address())
    price = factory.lazy_attribute(lambda a: randint(1, 100))


class CommentFactory(factory.DjangoModelFactory):
    """Factory for the comment model"""

    class Meta:
        model = models.Comments

    advertisement = factory.SubFactory(AdvertisementFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.lazy_attribute(lambda a: fake.text())


class ComplaintFactory(factory.DjangoModelFactory):
    """Factory for the complaint model"""

    class Meta:
        model = models.Complaints

    advertisement = factory.SubFactory(AdvertisementFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.lazy_attribute(lambda a: fake.text())
    confirmed = True


class ImageFactory(factory.DjangoModelFactory):
    """Factory for the Image model"""

    class Meta:
        model = models.Image

    advertisement = factory.SubFactory(AdvertisementFactory)
    image = factory.django.ImageField(color=fake.safe_color_name())
