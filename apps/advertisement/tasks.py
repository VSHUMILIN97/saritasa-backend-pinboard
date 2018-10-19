import logging

from celery import shared_task

from apps.advertisement.api.serializers.vk_post import VkPostSerializer
from apps.advertisement.views import send_to_wall_or_market
from apps.users.models import AppUser
from apps.utils.social_methods import vk_support_funcs as vk_support

__all__ = (
    'save_post_from_vk',
)

logger = logging.getLogger('django')


@shared_task()
def save_post_from_vk(entry_link, token):
    """ Create advert from user link data

    Args:
        entry_link: link to parse (vk only)
        token: external backend OAuth2 token

    Returns:
        id: Advertisement id created after task completion
    """
    vk_data = vk_support.get_vk_data(send_to_wall_or_market(entry_link, token))
    user = AppUser.objects.filter(access_token=token).first()
    vk_data['user'] = user.pk
    serializer = VkPostSerializer(
        data=vk_data
    )
    serializer.is_valid(raise_exception=True)
    advert = serializer.save()
    return advert.id
