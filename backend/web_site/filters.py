import django_filters as filter
from .models import Ingredient, Tag, Recipe


class RecipeFilter(filter.FilterSet):
    tag = filter.ModelMultipleChoiceFilter(field_name="tag_slug", to_field_name="slug", queryset=Tag.objects.all())
    is_favorite = filter.CharFilter(method="get_is_favorite")
    is_in_shopping_cart = filter.CharFilter(method="get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorite", "is_in_shopping_cart"]

    def get_is_favorite(self, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart_user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart_user=user)
        return Recipe.objects.all()


class IngredientFilter(filter.FilterSet):
    name = filter.CharFilter(field_name="name", lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ("name", )
