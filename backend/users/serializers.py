from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueTogetherValidator

from web_site.models import Recipe
from . import models


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
                and not self.context['request'].user.is_anonymous):
            return models.Follow.objects.filter(user=self.context['request'].user,
                                            following=obj).exists()
        return False


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    # в запросе обязательно должен быть пароль
    current_password = serializers.CharField(required=True)

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    class Meta:
        model = models.User
        fields = "__all__"


"""Рецепт без ингредиентов"""
class RecipeWithOutIngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )


class TokenSerializer(serializers.ModelSerializer):
    # source="key" означает, что в таблице token будет заполнено key
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
        fields = (
            "user",
            "following"
        )
        model = models.Follow
        """Проверка на уникальность"""
        validators = [UniqueTogetherValidator(queryset=models.Follow.objects.all(),
                                              fields=["user", "following"], )]


class ShowFollowerSerializer(serializers.ModelSerializer):
    recipes = RecipeWithOutIngredientsSerializer(many=True, required=True)
    is_subscribed = serializers.SerializerMethodField("if_is_subscribed")
    recipes_count = serializers.SerializerMethodField("get_recipes_count")

    class Meta:
        model = models.User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count"
        )

    """obj - подписчик, проверка пользователя на подписку"""

    def if_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return models.Follow.objects.filter(user=request.user, following=obj).exists()

    def get_recipes_count(self, obj):
        count = obj.recipes.all().count()
        return count
