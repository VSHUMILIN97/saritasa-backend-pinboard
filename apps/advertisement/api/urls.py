from django.conf.urls import url
from django.urls import path

from .views import (
    FavouritesRead,
    FavouriteView,
    VkImportAdsGetResultsView,
    VkImportAdsView,
)

urlpatterns = [
    url(
        r'^ads/import/vk/?$',
        VkImportAdsView.as_view(),
        name='vk-import-endpoint'
    ),
    url(
        r'^ads/import/vk/(?P<task_id>.*)$',
        VkImportAdsGetResultsView.as_view(),
        name='vk-import-get-results-endpoint'
    ),
    path('ads/<int:pk>/favourite', FavouriteView.as_view(
        {
            'post': 'create',
            'delete': 'destroy'
        }
    )),

    url(
        r'ads/favoured',
        FavouritesRead.as_view(),
        name='favourite-ads'
    ),

]
