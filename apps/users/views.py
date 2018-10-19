from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.advertisement.models import Advertisement
from apps.users.models import AppUser


class ProfileView(LoginRequiredMixin, TemplateView):
    """ User profile view """
    template_name = 'profile/account_profile.html'

    def get_context_data(self, **kwargs):
        """ Retrieving data from the DB and display it in the context """
        context = super().get_context_data()
        user_info = AppUser.objects.get(username=self.request.user.username)
        user_ads = Advertisement.objects.filter(user=self.request.user)
        user_info.fetch_user_screen_name_by_id()
        context['user'] = user_info
        context['user_ads'] = user_ads
        return context
