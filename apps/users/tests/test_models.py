from django.test import TestCase

from ..factories import SocialAuthUserFactory, UserFactory
from ..models import AppUser


class TestUser(TestCase):
    """Test for create a User.

    This test is testing AppUser model.

    """

    def setUp(self):
        self.user = UserFactory()
        self.sauser = SocialAuthUserFactory()

    def test_str_returns_username(self):
        """Test for correct object representation for __str__.

        User object should be return ``username``.

        """
        self.assertEqual(str(self.user), self.user.username)
        self.assertEqual(str(self.sauser), self.sauser.username)

    def test_create_user(self):
        """Test for user model.

        Checking for existance the created user.

        """
        user = AppUser.objects.filter(email=self.user.email)
        sauser = AppUser.objects.filter(email=self.sauser.email)

        self.assertEqual(user.exists(), True)
        self.assertEqual(sauser.exists(), True)

    def test_token_is_generated(self):
        """ Test for user model

        Checking for existance of generated token.

        """
        sauser = AppUser.objects.filter(access_token=self.sauser.access_token)
        self.assertTrue(sauser.exists())
