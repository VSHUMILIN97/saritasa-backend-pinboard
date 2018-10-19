import vk.exceptions as ex
from django.conf import settings

from apps.users.models import AppUser
from apps.utils.social_methods import exceptions as social_exceptions
from apps.utils.social_methods.vk_support_funcs import simulate_session


def setup_token(backend, user, response, *args, **kwargs):
    """ Pipeline of OAuth2 that write access token to the User Model

    Attributes:
        backend: OAuth app from the other side
        user: Current user instance (who invoked the auth via Socials)
        response: Response from backend side
        *args: Additional list of the positional arguments
        **kwargs: Additional dict of the keyword arguments
    """
    if backend.name == settings.SOCIAL_AUTH_VK_BACKEND:
        profile = AppUser.objects.get(username=user.username)
        social = user.social_auth.get(provider=settings.SOCIAL_AUTH_VK_BACKEND)
        token = social.extra_data['access_token']
        profile.access_token = token
        profile.save()


def change_name_on_id(backend, user, response, *args, **kwargs):
    """ Function that will define a unique int number
        rather than string that can be changed in user settings

    Attributes:
        backend: OAuth app from the other side
        user: Current user instance (who invoked the auth via Socials)
        response: Response from backend side
        *args: Additional list of the positional arguments
        **kwargs: Additional dict of the keyword arguments
    """
    if backend.name == settings.SOCIAL_AUTH_VK_BACKEND:
        profile = AppUser.objects.filter(username=user.username)
        if not profile.first().username or len(profile) > 1:
            return
        social = user.social_auth.filter(
            provider=settings.SOCIAL_AUTH_VK_BACKEND
        ).first()
        profile = profile.first()
        token = social.extra_data['access_token']
        response = vk_response_user_info(token, user)
        if not isinstance(response, social_exceptions.VKAPIParseFail):
            profile.email = response[0]['id']
            profile.save()


def vk_response_user_info(token, user):
    """ Call to VK API method users.get
        It fetch data from their DBs and return actual username
        their ID and additional info (if requested)

    Args:
        token: access token for VK API (stored in our DB)
        user: user instance, so we can get user by his screen name

    Returns:
        response (list): data from VK if no exceptions risen
        VKAPIParseFail (cls): Custom error that signalise something went wrong
    """
    api_wrap = simulate_session(token)
    if api_wrap:
        try:
            response = api_wrap.users.get(user_ids=user.username)
        except (ex.AUTHORIZATION_FAILED, ex.ACCESS_DENIED, ex.INVALID_USER_ID):
            raise social_exceptions.VKAPIParseFail
        return response

    raise social_exceptions.VKAPIParseFail
