import django_filters as filters
from .models import Ingredient, Tag, Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name="tags__slug", to_field_name="slug", queryset=Tag.objects.all())
    is_favorited = filters.CharFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.CharFilter(method="get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            """favorite__user обращается к полю user в модели Favorite, и фильтрует рецепты, которые 
            связаны с указанным пользователем через эту модель"""
            return Recipe.objects.filter(favorite__user=user)
        return Recipe.objects.all()
        # return None

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart__user=user)
        return Recipe.objects.all()
        # return None


# class FavoriteListFilter(RecipeFilter):
#     def get_is_favorited(self, queryset, name, value):
#         user = self.request.user
#         if value:
#             # фильтрации по избранным рецептам
#             return queryset.filter(favorite__user=user)
#         # return super().get_is_favorited(queryset, name, value)
#         return None


# class FavoriteListFilter(RecipeFilter):
#     is_favorited = filters.CharFilter(method="filter_is_favorited")
#
#     def filter_is_favorited(self, queryset, name, value):
#         user = self.request.user
#         if value and user.is_authenticated:
#             return queryset.filter(favorite__user=user)
#         return queryset.none()


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ("name", )
