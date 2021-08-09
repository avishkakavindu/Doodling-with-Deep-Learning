from rest_framework import serializers, status
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

from api.models import Quiz

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'password']


