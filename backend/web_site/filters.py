import django_filters as filters
from .models import Ingredient, Tag, Recipe


class RecipeFilter(filters.FilterSet):
    tag = filters.ModelMultipleChoiceFilter(field_name="tag_slug", to_field_name="slug", queryset=Tag.objects.all())
    is_favorite = filters.CharFilter(method="get_is_favorite")
    is_in_shopping_cart = filters.CharFilter(method="get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorite", "is_in_shopping_cart"]

    def get_is_favorite(self, value):
        user = self.request.user
        if value:
            """favorite__user обращается к полю user в модели Favorite, и фильтрует рецепты, которые 
            связаны с указанным пользователем через эту модель"""
            return Recipe.objects.filter(favorite__user=user)
        # return Recipe.objects.all()
        return None

    def get_is_in_shopping_cart(self, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart_user=user)
        # return Recipe.objects.all()
        return None


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ("name", )
