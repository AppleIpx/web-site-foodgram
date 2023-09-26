from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"tag", TagView, basename="tag")
router.register(r"ingredients", IngredientView, basename="ingredients")
router.register(r"recipes", RecipeView, basename="recipes")

urlpatterns = [
    path("recipes/<int:recipe_id>/favorite", FavoriteView.as_view()),
    path("recipes/<int:recipe_id>/shopping_cart", ShoppingCartViewSet.as_view()),
    path("", include(router.urls)),
]
