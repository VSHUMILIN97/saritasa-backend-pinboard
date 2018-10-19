from django.contrib.auth import get_user_model
from rest_framework import serializers

from libs.api.serializers.fields import DateTimeFieldWithTZ


class CustomUserDetailSerializer(serializers.ModelSerializer):

    date_joined = DateTimeFieldWithTZ(read_only=True)
    last_login = DateTimeFieldWithTZ(read_only=True)

    class Meta:
        model = get_user_model()
        depth = 1
        exclude = (
            'password',
            'is_superuser',
            'is_staff',
            'is_active',
            'groups',
            'user_permissions'
        )
        read_only_fields = ('email', 'username', )
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }


class MyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        exclude = ('password', 'user_permissions', 'groups')
