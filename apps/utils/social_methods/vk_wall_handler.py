import apps.utils.social_methods.exceptions as social_exceptions

from .vk_support_funcs import (
    VKWallPostItem,
    link_resolver,
    simulate_session,
    vk_exc,
)


# Celerisation
def fetch_data_from_wall_post(entry_link, token):
    """ Simple parser of the wall post in the VK.
        Getting its ID and using VK library to make API works.
        Then parse JSON or throw errors if needed

    Args:
        entry_link (str): Any chr sequence. Success result only if
                          link contains ?w=wall sequence in it
        token: user auth token (from registration)

    Returns:
        tuple: None if any errors occured, namedtuple for the success
        Contains - user's fullname, link to the photo and description

    Notes:
        Check vk_market_handler for the additional info about exceptions
        handling. It is impossible to note all of this stuff everywhere.

    """

    if not link_resolver(entry_link):
        raise social_exceptions.VKLinkIsDefective

    entry_link = entry_link.split(r'w=wall')
    api_wrap = simulate_session(token)

    if not api_wrap:
        raise social_exceptions.VKAPIParseFail
    try:
        # Call VK API methods via wrapper
        raw_txt_wall = api_wrap.wall.getById(posts=entry_link[1])

        """ Above call returns the following structure (JSON (loaded):
            There are a lot of missed fields, but only useful are stated
            [{
                "owner_id": -1,
                "text": "Some text",
                "marked_as_ads": 1, (<- this field is SO optional)
                "attachments": [{
                            "photo": {
                            "id": 422933443,
                            "owner_id": 36555,
                            "sizes": [{
                                        "type": "m",
                                        "url": "link.jpg",
                                        "width": 130,
                                        "height": 46
                                        },
                                        {
                                        lasts until max w/h is not reached
                                        }],
                Some another unused and probably unneeded fields
            }]
            It is possible to get marked_as_ads field so we need to check it.
            If so, all fields stored in copy_history field except owner_id
            (which is obviously -1, because it is VK itself). Type []
        """

        id_from_wall_post = raw_txt_wall[0]['owner_id']
        mark_ads = raw_txt_wall[0].get('marked_as_ads')

        # Stub for completion the function. Owner is Pavel Durov (which is not
        # True) according to mail.ru :)
        if mark_ads is not None:
            id_from_wall_post *= -1

        raw_txt_user = api_wrap.users.get(id=id_from_wall_post)
    except (IndexError, vk_exc.VkAPIError):  # noqa
        raise social_exceptions.VKIncorrectCredentials

    # User field is not in use right now. But we still define it, because it
    # may become handy.

    user = f"{raw_txt_user[0]['first_name']} {raw_txt_user[0]['last_name']}"

    if mark_ads is not None:
        copy_history = raw_txt_wall[0]['copy_history'][0]
        description = copy_history['text']
        photos = (
            copy_history['attachments'][0]['link']['photo']['photo_1280']
        )
        return VKWallPostItem(
            user=user,
            desc=description,
            photos=photos
        )

    else:
        # getting the photos (of the max size)
        photos = [each['photo']['sizes'][-1]['url']
                  for each in raw_txt_wall[0]['attachments']]
        description = raw_txt_wall[0]['text']

    return VKWallPostItem(
        user=user,
        desc=description,
        photos=photos[:5],
    )
