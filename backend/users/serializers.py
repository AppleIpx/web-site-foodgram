from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from . import models
from .models import User
from web_site.models import Recipe
from rest_framework.authtoken.models import Token
from .models import Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    # в запросе обязательно должен быть пароль
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = "__all__"


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "coking_time",)


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ("token",)


class FollowerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.all())
    following = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.all())

    def validate(self, data):
        user = data.get("user")
        following = data.get("following")
        if user == following:
            raise serializers.ValidationError("Нельзя на себя подписаться")
        return data

    class Meta:
        fields = ("user", "following")
        model = Follow
        """Проверка на уникальность"""
        validators = [UniqueTogetherValidator(queryset=Follow.objects.all(),
                                              fields=["user", "following"], )]


class ShowFollowerSerializer(serializers.ModelSerializer):
    recipes = FavoriteRecipeSerializer(serializers.ModelSerializer)
    is_subscribed = serializers.SerializerMethodField("check_if_is_subscribed")
    recipes_count = serializers.SerializerMethodField("get_recipes_count")

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subcribed", "recipes", "recipes_count")

    """obj - подписчик, проверка пользователя на подписку"""

    def if_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, following=obj).exists()

    def get_reipes_count(self, obj):
        count = obj.recipes.all().count()
        return count
