import vk.exceptions
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.utils.social_methods.vk_support_funcs import simulate_session
from libs import utils

__all__ = [
    'AppUser'
]

# Solution to avoid unique_together for email
AbstractUser._meta.get_field('email')._unique = True


# TODO: remove redundant function
def upload_user_media_to(instance, filename):
    """Upload media files to this folder.

    Returns:
        String. Generated path for image.

    """
    return '{name}/{id}/{filename}'.format(
        name=instance.__class__.__name__.lower(),
        id=instance.id,
        filename=utils.get_random_filename(filename)
    )


class AppUser(AbstractUser):
    """Custom user model.

    Attributes:
        first_name (str): first name
        last_name (str): last name
        username (str): username (not used)
        email (str): email (should be unique), this is our username field
        is_staff (bool): designates whether the user can log into
            this admin site
        is_active (bool): designates whether this user should be
            treated as active
        date_joined (datetime): when user joined
    """

    # so authentication happens by email instead of username
    # and username becomes sort of nick
    # ULTRA IMPORTANT NOTE:
    # It is not obvious, but email in our system equals VK user id
    # Why? Because.
    USERNAME_FIELD = 'email'

    # Make sure to exclude email from required fields if authentication
    # is done by email
    REQUIRED_FIELDS = ['username']

    # Used for saving OAuth access_token for the further work with it
    access_token = models.CharField(max_length=120, default=0)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

# TODO: this functionality required to be moved into Celery
    def fetch_user_screen_name_by_id(self, *args, **kwargs):
        """ Fetching user screen_name from VK API """
        api_wrap = simulate_session(self.access_token)
        try:
            response = api_wrap.users.get(
                user_ids=self.email,
                fields='screen_name'
            )
        except (
            vk.exceptions.VkAPIError,
            vk.exceptions.VkAuthError,
        ):
            """ We cant just crash in the middle of the DB Query,
             so response become None and should be checked before assigning """
            response = None

        try:
            screen_name = response[0]['screen_name']
        except (ValueError, KeyError, IndexError, TypeError):
            """ The same reason here. Check the above comment """
            screen_name = self.username

        if screen_name != self.username:
            self.username = screen_name
            super(AppUser, self).save(*args, **kwargs)
