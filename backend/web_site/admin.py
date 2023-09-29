from django.contrib import admin
from .models import Tag
from . import models


# admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
# @admin.register(models.Ingredient)


class IngredientInAdmin(admin.TabularInline):
    model = models.Recipe.ingredients.through
    # class IngredientAdmin(admin.ModelAdmin):
    #     list_display = ('name',)
    #     list_filter = ('name',)

@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInAdmin, ]

    class RecipeAdmin(admin.ModelAdmin):
        list_display = ('name', 'author', 'pub_date')
        list_filter = ('name', 'author', 'tags',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('title', 'author', 'pub_date')
#     list_filter = ('title', 'author', 'tag', )


# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('name', )
#     list_filter = ('name',)
