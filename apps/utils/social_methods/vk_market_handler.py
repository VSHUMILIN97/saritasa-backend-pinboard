from djmoney.money import Money

from apps.utils.social_methods import exceptions as social_exceptions
from .vk_support_funcs import (
    VKMarketItem,
    link_resolver,
    simulate_session,
    vk_exc,
)


# Celerisation
def fetch_data_from_market(entry_link, token):
    """ Simple parser of the market post in the VK.
        Getting its ID and using VK library to make API works.
        Then parse JSON or throw errors if needed

    Args:
        entry_link (str): Any chr sequence. Success result only if
                          link contains ?w=wall sequence in it
        token: user auth token (from registration)

    Returns:
        tuple: None if any errors occurred, namedtuple for the success
        Contains - user's fullname, link to the photo, description,
        price and title for the market post
    """
    if not link_resolver(entry_link):
        raise social_exceptions.VKLinkIsDefective

    entry_link = entry_link.split(r'w=product')
    api_wrap = simulate_session(token)

    if isinstance(api_wrap, social_exceptions.VKIncorrectCredentials):
        """ Still think this block will never be triggered
            Check vk_support_funcs module for the additional info
        """
        raise social_exceptions.VKIncorrectCredentials

    try:
        # First API call for fetching market info
        # extended = 1 means that we are also about to get photos
        raw_txt_market = api_wrap.market.getById(
            item_ids=f"{entry_link[1].replace('%2Fquery', '')}",
            extended=1
        )['items'][0]

        """ Code above returns following structure (JSON (loaded)):
            {
                "count": 1,
                "items": [{
                "id": 250407,
                "owner_id": -124527492,
                "title": "Spotty",
                "description": "A tail wagging champion",
                "price": {
                        "amount": "100000",
                        "currency": {
                        "id": 643,
                        "name": "RUB"
                            },
                        },
                "thumb_photo": "https://pp.vk.me/...6e5/1OWGz65-8vw.jpg",

                Other fields are unused and not important
            ........
            }]}
        """

        # Second API call for fetching group info
        # For now it is redundant though
        owner_eq_user = api_wrap.groups.getById(
            group_id=str(raw_txt_market['owner_id']).replace('-', '')
        )[0]
    except (IndexError, vk_exc.VkAPIError):
        # As it was said previously it is still possible to crash vk
        # if there are incorrect credentials.
        return social_exceptions.VKIncorrectCredentials

    group_user = (f"{owner_eq_user['screen_name']} - "
                  f"{owner_eq_user['name']}")

    # Cannot use Money from django money straight,
    # because VK split thousands by comma, not dot
    price = Money(
        amount=int(raw_txt_market['price']['amount']
                   .replace(',', '')) / 100,
        currency=raw_txt_market['price']['currency']['name']
    )

    # getting the photos (of the max size)
    photos = [each['sizes'][-1]['url'] for each in raw_txt_market['photos']]

    return VKMarketItem(
        user=group_user,
        desc=raw_txt_market['description'],
        photos=photos,
        title=raw_txt_market['title'],
        price=price
    )
