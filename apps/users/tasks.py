import logging
import time

from celery import shared_task
from django.conf import settings
from social_django.models import UserSocialAuth

from apps.users.models import AppUser
from apps.utils.social_methods.exceptions import VKIncorrectCredentials
from apps.utils.social_methods.vk_support_funcs import simulate_session

__all__ = (
    'test_celery',
    'fetch_user_data_from_vk',
)

logger = logging.getLogger('django')


@shared_task()
def test_celery(param):
    logger.info('Celery alive: %s', param)
    return param


@shared_task(ignore_result=True)
def fetch_user_data_from_vk(token, user_id):
    api_wrap = simulate_session(token)
    if isinstance(api_wrap, VKIncorrectCredentials):
        """
        Still think this block will never be triggered
        Check vk_support_funcs module for the additional info
        """
        raise VKIncorrectCredentials
    json_response = api_wrap.users.get(id=user_id)
    name = json_response[0]['first_name']
    surname = json_response[0]['last_name']
    create_user_entries.delay(user_id, name, surname, token)
    logger.info(f'Data for id{user_id} successfully fetched')


@shared_task(ignore_result=True)
def create_user_entries(user_id, name, surname, token):
    user = AppUser(
        email=user_id,
        first_name=name,
        last_name=surname,
        access_token=token
    )
    user.save()
    logger.info(f'Local user for {user_id} successfully created')
    social_user = UserSocialAuth(
        user=user,
        uid=user_id,
        provider=settings.LOCAL_BACKENDS_ASSOC_SOCIAL_BACKENDS['vk'],
        extra_data={
            "id": user_id,
            "expires": 0,
            "auth_time": time.time(), "token_type": 'null',
            "access_token": token
        }
    )
    social_user.save()
    logger.info(f'Social user for {user_id} created successfully')
