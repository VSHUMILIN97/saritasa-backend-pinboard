from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.advertisement.models import Advertisement


class VkLinkSerializer(serializers.Serializer):
    url = serializers.URLField(
        max_length=250,
        min_length=25,
        allow_blank=False,
        required=True,
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)


class TaskNameForVkSerializer(serializers.Serializer):
    task_id = serializers.CharField(
        max_length=40,
        min_length=38
    )

    def validate_task_id(self, value):
        if not value.endswith('-vk'):
            raise serializers.ValidationError(_('Incorrect task id'))
        return value


class VkPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advertisement
        fields = ('user', 'description', 'price', 'title',)

    def create(self, validated_data):
        return Advertisement.objects.create(**validated_data, published=False)
