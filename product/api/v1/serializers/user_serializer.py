from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'course', 'start_date', 'end_date')
