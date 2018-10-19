import urllib.request
from datetime import datetime

import django_filters
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from taggit.models import Tag

from apps.utils.social_methods import vk_market_handler, vk_wall_handler
from apps.utils.social_methods.vk_support_funcs import get_vk_data
from .forms import AdvertisementForm, ImageFormSet
from .models import Advertisement, Comments, Complaints, Image


def send_to_wall_or_market(entry_link, token):
    """ Choose which function will handle parsing """
    if '?w=wall' in entry_link:
        return vk_wall_handler.fetch_data_from_wall_post(entry_link, token)
    else:
        return vk_market_handler.fetch_data_from_market(entry_link, token)


class AdvertisementsList(ListView):
    """Show the list of adverts"""

    template_name = 'advertisements/advertisements_list.html'
    queryset = Advertisement.objects.all().exclude(published=False)
    context_object_name = 'adverts'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        """ Adding filters to the AdList page """
        context = super().get_context_data()
        context['all_tags'] = Tag.objects.all()
        filter = AdvertFilter(self.request.GET, self.queryset)
        context['filter'] = filter
        context['parsed_adverts'] = filter.qs
        return context


class AddAdvertisement(LoginRequiredMixin, CreateView):
    """Create a form to add a new advert

    If it is a GET request, view just simply drops all initials
    in the form and makes sure GET of super is called

    If it is POST request, view specifies input that invoked
    this view and then:

     If it is VK fetcher - adds initials

     If it is post advert - checks that form is valid and create ad

     If something else - returns errors
    """

    form_class = AdvertisementForm
    template_name = 'advertisements/add_advertisement.html'

    # View should not save broken tags
    def get(self, request, *args, **kwargs):
        """ Set initial tags for the template """
        self.initial = {'all_tags': Tag.objects.all()}
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """"Get formset as a context

        This method gets an empty ImageFormSet to be
        filled in by a user
        """
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            # a formset to add several images
            data['formset_image'] = ImageFormSet(
                self.request.POST,
                self.request.FILES
            )
        else:
            data['formset_image'] = ImageFormSet()

        return data

    def post(self, request, *args, **kwargs):
        # if a user uses VK for adding a new advert
        if 'vk_link' in request.POST:
            # we add it through a special method and get the advert's id also
            advert_id = self.save_vk_advert()
            # after creating an advert we direct a user to edit it
            return HttpResponseRedirect(
                reverse('edit-advert', args=[advert_id])
            )

        # or we add it through a form
        else:
            form = AdvertisementForm(request.POST)
            if form.is_valid():
                return self.form_valid(form)

    def save_vk_advert(self):
        """Save an advertisement from VK"""

        # get VK data

        parse_result = send_to_wall_or_market(
            self.request.POST.get('vk_link', ''),
            self.request.user.access_token
        )

        vk_data = get_vk_data(parse_result)

        # Saving photo to the temporary storage and then link it to form
        vk_data['photos'] = []
        for photo_link in parse_result.photos:
            try:
                image, _ = urllib.request.urlretrieve(photo_link)
            except (ConnectionError, OSError, TypeError):
                # If link is a path to a Storage file
                #  or there are no connection,
                # then set image as none and crash context manager later
                image = None
            vk_data['photos'].append(image)

        # add tags to our advert
        vk_data['all_tags'] = Tag.objects.all()

        # Creating an advert by the data we got

        advert = Advertisement.objects.create(
            user=self.request.user,
            title=vk_data['title'],
            description=vk_data['description'],
            price=vk_data['price'],
            address=settings.DEFAULT_ADDRESS
        )

        # Saving all images for it

        for each in vk_data['photos']:
            img = Image.objects.create(
                advertisement=advert,
            )
            # save the file uniquely
            img.image.save(
                f'image_{advert.id}_{img.id}_{each[8:]}.jpg',
                open(each, 'rb')
            )

        return advert.id

    def form_valid(self, form):
        """ CreateView basic realisation of form validation """

        # here we specify the advert's creator
        form.instance.user = self.request.user

        with transaction.atomic():

            response = super().form_valid(form)

            images = ImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )

            if images.is_valid():

                images.save()

            return response


class AdvertisementPage(TemplateView):
    """Show an advert's information or add comments/complaints"""

    template_name = 'advertisements/advertisement_page.html'

    def get_context_data(self, **kwargs):
        """Show an advert's information"""

        # an instance of advertisements we are going to show
        advert = Advertisement.objects.get(id=kwargs['id'])
        # take comments that are related to this advert
        comments = advert.comments_set.all()
        # take complaints that are related to this advert
        complaints = advert.complaints_set.all()
        # take all the photos in formset
        photos = [
            each.initial['image']
            for each in ImageFormSet(instance=advert)
            if each.changed_data
        ]
        ctx = {
            'advert': advert,
            'photos': photos,
            'comments': comments,
            'complaints': complaints,
        }
        return ctx

    def post(self, request, **kwargs):
        """Add comments/complaints"""

        # id of the advert we target
        advert_id = kwargs['id']

        # if a user entered the comment field in HTML
        if request.POST.get('comment_text'):

            self.add_comment(
                advert_id,
                self.request.user,
                self.request.POST.get('comment_text')
            )

        # or if a user entered the complaint field in HTML
        elif request.POST.get('complaint_text'):

            self.add_complaint(
                advert_id,
                self.request.user,
                self.request.POST.get('complaint_text')
            )

        return HttpResponseRedirect(
            reverse('info', args=[advert_id])
        )

    @staticmethod
    def add_comment(advert_id, user, text):
        """Add a comment"""

        Comments.objects.create(
            user=user,
            text=text,
            advertisement=Advertisement.objects.get(id=advert_id),
            created_date=datetime.now()
        )

    @staticmethod
    def add_complaint(advert_id, user, text):
        """Add a complaint"""

        Complaints.objects.create(
            user=user,
            text=text,
            advertisement=Advertisement.objects.get(id=advert_id),
            created_date=datetime.now(),
        )


class EditAdvertisement(UpdateView):
    """Edit adverts"""

    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'advertisements/edit-advertisement.html'

    def get_context_data(self, **kwargs):
        """Get the filled in formset as a context"""

        kwargs['image_formset'] = ImageFormSet(
            instance=Advertisement.objects.get(
                id=self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
        kwargs['all_tags'] = Tag.objects.all()

        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """Let users edit only their adverts"""
        qs = super().get_queryset()

        # replace this with whatever makes sense for your application
        return qs.filter(user=self.request.user)


class TagsFilter(django_filters.filters.CharFilter):
    """ Create a special M2M filter for the tags field from taggit module """

    def filter(self, qs, value):
        """ Logic of the filter

        Returns:
            queryset: It will be the same before filtering if value of the
            input in None, else qs will be filtered with special __name__in
            filter. Because tags are stored as list []
        """
        if not value:
            return qs
        tags = (tag.strip().capitalize() for tag in value.split(','))
        qs = qs.filter(tags__name__in=tags).distinct()

        return qs


class AdvertFilter(django_filters.FilterSet):
    """ Create filter for advertisements w/ usage FilterSet """

    tags = TagsFilter()

    class Meta:
        model = Advertisement
        fields = {
            'price': ['lte', 'gte'],
            'title': ['icontains'],
            'created_date': ['lte', 'gte'],
        }


class EditImage(View):
    """The method gets an image formset to change and then goes to editing"""

    def post(self, request, pk):
        form = ImageFormSet(
            request.POST,
            request.FILES,
            instance=Advertisement.objects.get(id=pk)
        )

        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('edit-advert', args=[pk]))
