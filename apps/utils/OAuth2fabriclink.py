
class LinkFabric(object):
    """ Fabric link for the OAuth2"""

    def __init__(
        self,
        *,
        social_app=None,
        client_id=None,
        redirect_uri=None
    ):
        """ Initials for LinkFabric

        Args:
            social_app: URI for the OAuth2 API backend
            client_id: stored inside an app
            redirect_uri: callback url (request.get_host())
        """
        self.client_id = client_id
        self.social_app = social_app
        self.redirect_uri = redirect_uri

    def __getattr__(self, item):
        return None

    def factor_link(self):
        """ Factor link from inner variables """
        body = ''
        for index, key in enumerate(self.__dict__.keys()):
            if key in ('secure', 'social_app'):
                continue
            if body and key:
                body += f'&{key}={str(self.__dict__[key]).replace(" ", "")}'
            elif key:
                body += f'?{key}={str(self.__dict__[key]).replace(" ", "")}'

        return f'https://{self.social_app}{body}'

    def __repr__(self):
        return None

    def __str__(self):
        return None
