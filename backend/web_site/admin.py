from django.contrib import admin
from . import models


class IngredientInAdmin(admin.TabularInline):
    model = models.Recipe.ingredients.through


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'cooking_time', 'text', "in_favorites", 'image', 'author', )
    list_editable = ('name', 'cooking_time', 'text', 'image', 'author',)
    readonly_fields = ('in_favorites',)
    list_filter = ('name', 'author',)
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite.count()

    in_favorites.short_description = "В избранном"


@admin.register(models.IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    ordering = ("user",)


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe', )
    list_editable = ('user', 'recipe', )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', 'pk')
    list_editable = ('color', 'slug')
    list_display_links = ('name',)
    empty_value_display = '-пусто-'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'pk')
    list_filter = ('name',)
    search_fields = ('name',)
