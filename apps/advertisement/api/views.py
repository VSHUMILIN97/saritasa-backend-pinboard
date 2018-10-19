from celery.result import AsyncResult
from celery.utils import uuid
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.advertisement.api.serializers.favourites import AdFavouriteSerializer
from apps.advertisement.models import Advertisement
from apps.users.models import AppUser
from config.celery import app
from .serializers.vk_post import TaskNameForVkSerializer, VkLinkSerializer
from ..tasks import save_post_from_vk


class VkImportAdsGetResultsView(APIView):

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    """ Endpoint for previewing task results """
    def get(self, request, task_id, *args, **kwargs):
        """ GET API method

        Args:
            task_id: task id from POST request
        """
        serializer = TaskNameForVkSerializer(data={'task_id': task_id})
        serializer.is_valid(raise_exception=True)
        res = AsyncResult(task_id, app=app)
        return Response(
            {
                'job_id': task_id,
                'state': res.state,
                'advertisement': res.result
            }
        )


class VkImportAdsView(APIView):

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    """ Endpoint for the Ad posting """
    def post(self, request, *args, **kwargs):
        """ Auth user first """
        serializer = VkLinkSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        external_token = self.request.user.access_token
        task = save_post_from_vk.apply_async(
            args=[serializer.data['url'], external_token],
            task_id=f'{uuid()}-vk'
        )
        return Response(
            {'task_id': task.id},
            status=status.HTTP_201_CREATED
        )


class FavouriteView(viewsets.ViewSet):
    """ Favourite Add/Delete ViewSet """
    queryset = AppUser.objects.all()
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, pk):
        """ Create M2M relationship favourite with Ad ID"""
        ad = Advertisement.objects.filter(pk=pk)
        if not ad.exists():
            return Response(
                {'error': _(f'No ad with id {pk}')},
                status=status.HTTP_404_NOT_FOUND
            )
        self.request.user.user_favourites.add(ad[0])
        return Response(
            {'response': _(f'Added {pk} to you favourites')},
            status=status.HTTP_202_ACCEPTED
        )

    def destroy(self, request, pk=None):
        """ Remove M2M relationship favourite with Ad ID """
        ad = Advertisement.objects.filter(pk=pk)
        if not ad.exists():
            return Response(
                {'error': _(f'No ad with id {pk}')},
                status=status.HTTP_404_NOT_FOUND
            )
        self.request.user.user_favourites.remove(ad[0])
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class FavouritesRead(APIView):
    """ Get favourites APIView """
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """ Get all M2M relationships with this user"""
        fav_ads = self.request.user.user_favourites.all()
        serializer = AdFavouriteSerializer(fav_ads, many=True)
        return Response(serializer.data)
