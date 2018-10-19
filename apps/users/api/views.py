import json
import logging

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import Application
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_social_oauth2.views import ConvertTokenView, TokenView

from apps.users.tasks import fetch_user_data_from_vk
from apps.utils.OAuth2fabriclink import LinkFabric
from .serializers import auth

logger = logging.getLogger('django')

AppUser = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = AppUser.objects.all()
    serializer_class = auth.CustomUserDetailSerializer
    permission_classes = [AllowAny]


class LookupUserOptionsView(APIView):
    """
    Lookup class for getting list of available users
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = {
            user.username: user.username.title()
            for user in AppUser.objects.all()}
        return Response(usernames)


class WrappedConvertTokenView(ConvertTokenView):
    """ This wrapper fetch local backend from the POST request and then
        add special fields for the ConvertTokenView from the original
        lib rest_framework_social_oauth2
        param: token
        request type: POST
    """
    def post(self, request, local_backend, *args, format=None, **kwargs):
        """ Get copy of the request.POST and add additional
            body parameters to the given request.

        Args:
            request: common WSGI or ASGI request response
            local_backend: app backend for the auth/registration

        Returns:
            Response: JSON response from the server
        """
        request._request.POST = request._request.POST.copy()
        request._request.POST['backend'] = (
            settings.LOCAL_BACKENDS_ASSOC_SOCIAL_BACKENDS[local_backend]
        )
        server_app = Application.objects.filter(name=f'{local_backend}_app')
        if not server_app.exists():
            return Response(
                _({'error': 'Current backend is on maintenance'}),
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        server_app = server_app.first()
        request._request.POST['client_id'] = server_app.client_id
        request._request.POST['client_secret'] = server_app.client_secret
        request._request.POST['grant_type'] = settings.DRF_SOCIALS_GRANT_TYPE
        return super().post(request, *args, **kwargs)


class WrappedRefreshTokenView(TokenView):
    """ This wrapper fetch local backend from the POST request and then
        add special fields for the ConvertTokenView from the original
        lib rest_framework_social_oauth2
        param: refresh_token
        request_type: POST
    """
    def post(self, request, local_backend, *args, format=None, **kwargs):
        """ Get copy of the request.POST and add additional
            body parameters to the given request.

        Args:
            request: common WSGI or ASGI request response
            local_backend: app backend for the auth/registration

        Returns:
            Response: JSON response from the server
        """
        request._request.POST = request._request.POST.copy()
        server_app = Application.objects.filter(name=f'{local_backend}_app')
        if not server_app.exists():
            return Response(
                _({'error': 'Current backend is on maintenance'}),
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        server_app = server_app.first()
        request._request.POST['client_id'] = server_app.client_id
        request._request.POST['client_secret'] = server_app.client_secret
        request._request.POST['grant_type'] = settings.DRF_SOCIALS_REFRESH
        return super().post(request, *args, **kwargs)


class AuthSocialView(APIView):
    """ Class for auth or user registration via Social Auth """
    def get(self, request, local_backend, format=None):
        """ Check if backend in our backend-ecosystem and then return a
            response with body contains either link to proceed OAuth2 or error

        Attributes:
            local_backend: Url required arg. Name of the local app backend
        """
        current_url = f'http://{request.get_host()}{request.path_info}'

        # For the review: I guess I need to divide GET, so "mobile" backend
        # should request this view twice. Once to get form and code via GET
        # (because they do not provide us with any data) and then THEY should
        # call POST with code. Is this right or this implementation is OK?
        # If code is in GET request then we pass everything to POST request
        if request.GET.get('code'):
            return self.post(request, request.GET.get('code'), current_url)
        if not any([app_name in local_backend for app_name in
                    settings.LOCAL_SOCIAL_AUTH_APP_BACKENDS]):
            return Response(
                _({'error': (f'Cannot find {local_backend} in'
                             f' {settings.LOCAL_SOCIAL_AUTH_APP_BACKENDS}')}),
                status=status.HTTP_404_NOT_FOUND
            )

        name = f'{local_backend}_app'
        app = Application.objects.filter(
            name=name
        )

        # Can happen only server side if DB went offline or local app wasn't
        # yet created. Anyway, log it!
        if not app.exists():
            logging.error(
                f'Local backend {local_backend} is not created or unreachable'
            )

            return Response(
                _({'error': 'Current backend is on maintenance'}),  # :)
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        vk_link_code = LinkFabric(
            social_app=settings.VK_OAUTH2_AUTHORIZE_LINK + 'authorize',
            client_id=settings.SOCIAL_AUTH_VK_OAUTH2_KEY,
        )
        vk_link_code.scope = settings.SOCIAL_AUTH_VK_OAUTH2_SCOPE
        vk_link_code.response_type = 'code'
        vk_link_code.v = settings.VK_API_VERSION
        vk_link_code.redirect_uri = current_url
        return Response(
            {
                'auth_link': vk_link_code.factor_link(),
                'callback_uri': current_url
            }
        )

    def post(self, request, code, redirect_uri, format=None):
        """ POST method for the auto request for the external token

        Args:
            request: wsgi (asgi) request object
            code: auth code from external service

        Notes:
            Add correct documentation
        """
        vk_link_authorize = LinkFabric(
            social_app=settings.VK_OAUTH2_AUTHORIZE_LINK + 'access_token',
            client_id=settings.SOCIAL_AUTH_VK_OAUTH2_KEY,
        )
        vk_link_authorize.code = code
        vk_link_authorize.redirect_uri = redirect_uri
        vk_link_authorize.client_secret = settings.SOCIAL_AUTH_VK_OAUTH2_SECRET

        # I dunno what should I refactor here
        res = requests.post(vk_link_authorize.factor_link())
        data = json.loads(res.text)
        if data.get('error'):
            return Response(
                _({'error': data['error_description']}),
                status=status.HTTP_400_BAD_REQUEST
            )
        print(data)
        return Response(
            ({'token': data['access_token'], 'user_id': data['user_id']}),
            status=status.HTTP_200_OK
        )


class RegisterSocialView(APIView):
    """ Register logic of the local API OAuth endpoint """
    def post(self, request, format=None):
        """ Registration is VK only (for now or forever) """
        token = request.data.get('token')
        user_id = request.data.get('user_id')
        if not token:
            return Response(
                _({'error': f'Provide token from the VK OAuth2 server'}),
                status=status.HTTP_400_BAD_REQUEST
            )
        fetch_user_data_from_vk.delay(token, user_id)
        return Response(
            _({
                'response': 'User will be created within a few minutes or less'
            }),
            status=status.HTTP_201_CREATED
        )
