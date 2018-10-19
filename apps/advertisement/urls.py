from django.conf.urls import url

from . import views

urlpatterns = [
    # by default we show the list of adverts
    url(
        r'^$',
        views.AdvertisementsList.as_view(),
        name='list'
    ),
    # a page for creating new adverts
    url(
        r'^new-advert/$', views.AddAdvertisement.as_view(),
        name='new_ad'
    ),
    # a page of a particular advert with comments and complaints
    url(
        r'^advertisement/(?P<id>[0-9]+)/$',
        views.AdvertisementPage.as_view(),
        name='info'
    ),
    # a page for editing new adverts
    url(
        r'^edit-advert/(?P<pk>[\w-]+)/$',
        views.EditAdvertisement.as_view(),
        name='edit-advert'
    ),
    url(
        r'^edit-image/(?P<pk>[\w-]+)/$',
        views.EditImage.as_view(),
        name='edit-image'
    ),
]
