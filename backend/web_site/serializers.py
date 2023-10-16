from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserSerializer
from . import models


class TagSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = (
            "id",
            "name",
            "color",
            "slug"
        )


class IngredientInRecipeSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = models.IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount"
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit"
        )


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializers(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField("get_ingredients")
    is_favorited = serializers.SerializerMethodField("get_is_favorite")
    is_in_shopping_cart = serializers.SerializerMethodField("get_is_in_shopping_cart")

    class Meta:
        model = models.Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time"
        )

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
    id = serializers.IntegerField()

    # позволяет работать с первычными ключами

    class Meta:
        model = models.IngredientInRecipe
        fields = (
            "id",
            "amount"
        )


class CreateRecipeSerializers(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    # сохранение изображения в видде строки - ссылки
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializers(many=True)
    # many указывает на то, что будет много данных(список или множество)
    id = serializers.ReadOnlyField()
    tags = serializers.SlugRelatedField(many=True, queryset=models.Tag.objects.all(), slug_field="id")

    # queryset - это запрос к бд, который определяет откуда брать данные.

    class Meta:
        model = models.Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time"
        )

    def validate(self, obj):
        for field in ['name', 'text', 'cooking_time']:
            if not obj.get(field):
                raise serializers.ValidationError(f'{field} - Обязательное поле.')
        if not obj.get('tags'):
            raise serializers.ValidationError('Нужно указать минимум 1 тег.')
        if not obj.get('ingredients'):
            raise serializers.ValidationError('Нужно указать минимум 1 ингредиент.')
        inrgedient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError('Ингредиенты должны быть уникальны.')
        return obj

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            # Создаем запись в модели IngredientInRecipe
            models.IngredientInRecipe.objects.create(recipe=recipe,
                                                     ingredient=models.Ingredient.objects.get(pk=ingredient_id),
                                                     amount=amount
                                                     )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = models.Recipe.objects.create(author=self.context['request'].user,
                                              **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    # экземпляр модели
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        models.IngredientInRecipe.objects.filter(recipe=instance,
                                                 ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ShowRecipeSerializer(instance,
                                    context=self.context).data


class FavoriteSerializers(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=models.Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.all())

    class Meta:
        model = models.Favorite
        fields = (
            "recipe",
            "user"
        )


class TugInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = "__all__"


class ShoppingCartSerializers(FavoriteSerializers):
    class Meta:
        model = models.ShoppingCart
        fields = (
            "recipe",
            "user"
        )
