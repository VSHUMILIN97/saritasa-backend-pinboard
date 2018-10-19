from rest_framework import serializers

from apps.advertisement.models import Advertisement


class AdFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ('user', 'title', 'pk', 'published')
