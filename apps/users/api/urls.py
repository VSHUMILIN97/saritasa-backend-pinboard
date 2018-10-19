from uuid import uuid4

from django.conf.urls import url
from oauth2_provider.views import AuthorizationView
from rest_framework.routers import DefaultRouter
from rest_framework_social_oauth2 import views as rest_auth_views

from .views import (
    AuthSocialView,
    LookupUserOptionsView,
    RegisterSocialView,
    UsersViewSet,
    WrappedConvertTokenView,
    WrappedRefreshTokenView,
)

# register URL like
# router.register(r'users', UsersAPIView)
router = DefaultRouter()
router.register(r'users', UsersViewSet, base_name='user')
urlpatterns = router.urls

urlpatterns += [
    url(
        # authorize could be called by server with reverse(), but it's not
        # cool if it will be scammed at any case.
        r'^oauth/{0}{0}{0}/authorize/?$'.format(uuid4()),
        AuthorizationView.as_view(),
        # Pre-defined name by oauth2_provider lib, don't change it
        name='authorize'
    ),

    url(
        r'^lookup/users/$',
        LookupUserOptionsView.as_view()
    ),
    # Exchange external token for ours
    url(
        r'^oauth/(?P<local_backend>.*)/convert-token/?$',
        WrappedConvertTokenView.as_view(),
        name='convert_token'
    ),
    url(
        r'^oauth/(?P<local_backend>.*)/refresh-token/?$',
        WrappedRefreshTokenView.as_view(),
        name='refresh_token'
    ),
    # Revoke our internal token
    url(
        r'^oauth/revert-token/?$',
        rest_auth_views.RevokeTokenView.as_view(),
        name='revoke_token'
    ),
    # Get token from external backend for the local backend
    url(
        r'^oauth/(?P<local_backend>.*)/auth/$',
        AuthSocialView.as_view(),
        name='auth-social-local'
    ),
    # Register user in our system with external backend token
    url(
        r'^oauth/register/?$',
        RegisterSocialView.as_view(),
        name='register-social-local'
    )

]
