from rest_framework import serializers
from web_site.models import Ingredient, Tag
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
    unit = serializers.ReadOnlyField(source='ingredient.unit')

    class Meta:
        model = models.IngredientInRecipe
        fields = ("id", "name", "unit", "quantity")


class AddIngredientToRecipeSerializers(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # позволяет работать с первычными ключами

    class Meta:
        model = models.IngredientInRecipe
        fields = ("id", "quantity")


class CreateRecipeSerializers(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    # сохранение изображения в видде строки - ссылки
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializers(many=True)
    # many указывает на то, что будет много данных(список или множество)
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(many=True, queryset=models.Tag.objects.all(), slug_field="id")

    # queryset - это запрос к бд, который определяет откуда брать данные.
    # slug_field - поле, которое будет использоваться для связывания с тегами

    class Meta:
        model = models.Recipe
        fields = ["id", "tags", "author", "ingredients", "name", "image", "description", "cooking_time"]

    def validate_coking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError("Введено некорректное время <0")
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        # это данные, которые были переданы в запросе и уже были проверены и преобразованы в сериализаторе
        author = self.context.get("request").user
        #извлечение из запроса авторизации пользователя.
        recipe = models.Recipe.objects.create(author=author, **validated_data)
        # создаем экземпляр модели Recipe, в котором указываем автора и все остальные(**) данные из validated_data
        for infredient in ingredients_data:
            infredient_mode = infredient["id"]
            quantity = infredient["quantity"]
            models.IngredientInRecipe.objects.create(infredient=infredient_mode, recipe=recipe, quantity=quantity)
        # в цикле происходит создание связей через модель IngredientInRecipe и для каждого ингредиента
        # в ingredients_data создается связь с рецептом указывая infredient_mode и quantity
        recipe.tags.set(tags_data)
        # здесь устанавливается связь между рецептом и тегами
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
            quantity = ingredient["quantity"]
            models.IngredientInRecipe.objects.create(ingredient=ingredient_update, recipe=instance, quantity=quantity)
            # тут происходит создание новых связей между рецептом и ингредиентами
            # цикл перебирает переданные ингредиенты и создает записи в модели(IngredientInRecipe), указывая
            # к какому рецепту они относятся
            instance.name = validated_data.pop("name")
            instance.description = validated_data.pop("description")
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
        fields = ["recipe", "user"]
