import uuid

from django.utils import timezone

import factory

from .models import AppUser


class UserFactory(factory.DjangoModelFactory):
    """Factory for generates test User model.

    There are required fields first_name, last_name, username and email.

    """

    class Meta:
        model = AppUser

    @factory.lazy_attribute
    def username(self):
        return "user_{0}".format(uuid.uuid4())

    @factory.lazy_attribute
    def email(self):
        return "{0}@example.com".format(self.username)


class AdminUserFactory(UserFactory):
    """Factory for generates test User model with admin's privileges """
    class Meta:
        model = AppUser

    is_superuser = True
    is_staff = True


class SocialAuthUserFactory(factory.DjangoModelFactory):
    """ Factory that generates User after Social Auth entry (w/ token) """
    class Meta:
        model = AppUser

    @factory.lazy_attribute
    def access_token(self):
        """ Just so random """
        return "tok_{0}".format(uuid.uuid4())

    date_joined = factory.LazyFunction(timezone.now)
    is_staff = False
    is_active = True
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.LazyAttribute(lambda x: f'{x.access_token}@vk.com')
    email = factory.LazyAttribute(lambda x: f'{x.date_joined}@email.org')
