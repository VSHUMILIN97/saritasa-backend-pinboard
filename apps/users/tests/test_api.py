import unittest

from rest_framework import status
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from faker import Faker

from ..api.views import CheckUsernameView
from ..factories import UserFactory

fake = Faker()


class TestAPIUser(APITestCase):
    """Test for API of ``users`` app.

    Contains tests for and user exists.

    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = UserFactory()

    def _get_response_for_username_api(self, url, username):
        request = self.factory.get(url.format(username=username))

        force_authenticate(request, user=self.user)

        return CheckUsernameView.as_view()(request, username=username)

    def _get_response_for_password_api(self, data):
        url = '/api/v1/auth/password/reset/'

        self.client.force_authenticate(user=self.user)

        return self.client.post(url, data, format='json')

    @unittest.skip("FIX")
    def test_username_api(self):
        """Test for username existance.

        Raise http 404 if username already registered and 200 if does not.

        """
        url = '/api/v1/auth/check/{username}/'

        # if username exists
        username = self.user.username
        response = self._get_response_for_username_api(url, username)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # if username does not exists
        username = fake.user_name()
        response = self._get_response_for_username_api(url, username)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
