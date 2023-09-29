from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from web_site.models import Ingredient, Tag, Recipe
from users.serializers import UserSerializer
from . import models
from drf_extra_fields.fields import Base64ImageField


class TagSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ["id", "name", "color", "slug", ]


class IngredientInRecipeSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    # unit = serializers.ReadOnlyField(source='ingredient.unit')
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = models.IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ["id", "name", "measurement_unit"]


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializers(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField("get_ingredients")
    is_favorite = serializers.SerializerMethodField("get_is_favorite")
    is_in_shopping_cart = serializers.SerializerMethodField("get_is_in_shopping_cart")

    class Meta:
        model = models.Recipe
        fields = ["id", "tags", "author", "ingredients", "is_favorite", "is_in_shopping_cart",
                  "name", "image", "text", "cooking_time", ]

    def get_ingredients(self, obj):
        ingredients = models.IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializers(ingredients, many=True).data

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return models.Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return models.ShoppingCart.objects.filter(recipe=obj, user=user).exists()


class AddIngredientToRecipeSerializers(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=models.Ingredient.objects.all())
    # позволяет работать с первычными ключами

    class Meta:
        model = models.IngredientInRecipe
        fields = ("id", "amount",)


class CreateRecipeSerializers(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    # сохранение изображения в видде строки - ссылки
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializers(many=True)
    # ingredients = SerializerMethodField()
    # many указывает на то, что будет много данных(список или множество)
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(many=True, queryset=models.Tag.objects.all(), slug_field="id")

    # queryset - это запрос к бд, который определяет откуда брать данные.
    # slug_field - поле, которое будет использоваться для связывания с тегами

    class Meta:
        model = models.Recipe
        fields = ["id", "tags", "author", "ingredients", "name", "image",
                  "text", "cooking_time"]

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError("Введите число больше 0")
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")

        # Создание рецепта с автором и остальными данными
        author = self.context.get("request").user
        recipe = models.Recipe.objects.create(author=author, **validated_data)

        # Создание связей между рецептом и ингредиентами
        for ingredient in ingredients_data:
            ingredient_model = ingredient["id"]
            amount = ingredient["amount"]
            models.IngredientInRecipe.objects.create(
                ingredient=ingredient_model, recipe=recipe, amount=amount
            )
        recipe.tags.set(tags_data)
        return recipe



    """Метод берет данные данные из запроса и создает новый рецепт и связанные с ним ингредиенты 
    и теги, а затем возвращает созданный рецепт"""

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        # происходит извлечение данных об ингредиентах и тегах
        models.TagsInRecipe.objects.filter(recipe=instance).delete()
        models.IngredientInRecipe.objects.filter(recipe=instance).delete()
        # удаляются все связи между текущим рецептом(instance) и тегами и ингредиентами в бд
        for ingredient in ingredients_data:
            ingredient_update = ingredient["id"]
            amount = ingredient["amount"]
            models.IngredientInRecipe.objects.create(ingredient=ingredient_update, recipe=instance, amount=amount)
            # тут происходит создание новых связей между рецептом и ингредиентами
            # цикл перебирает переданные ингредиенты и создает записи в модели(IngredientInRecipe), указывая
            # к какому рецепту они относятся
            instance.name = validated_data.pop("name")
            instance.text = validated_data.pop("text")
            if validated_data.get("image") is not None:
                instance.image = validated_data.pop("image")
            instance.cooking_time = validated_data.pop("cooking_time")
            instance.tag.set(tags_data)
            # тут обновление полей рецепта на основе переданных данных
            instance.save()
            # сохранение экземпляра рецепта в бд
            return instance


class FavoriteSerializers(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=models.Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.all())

    class Meta:
        model = models.Favorite
        fields = ["recipe", "user", ]


class TugInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class ShoppingCartSerializers(FavoriteSerializers):
    class Meta:
        model = models.ShoppingCart
        fields = ["recipe", "user", ]
