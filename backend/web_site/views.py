from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAuthorOrReadOnly
from . import serializers, models


class TagView(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializers
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngredientsView(viewsets.ModelViewSet):
    queryset = models.Ingredient.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = serializers.IngredientSerializer
    filter_backends = [DjangoFilterBackend, ]
    search_fields = ["name", ]
    pagination_class = None

    def get_queryset(self):
        name = str(self.request.query_params.get("name"))
        queryset = self.queryset
        if not name:
            return queryset
        start_queryset = queryset.filter(name__istartswith=name)
        return start_queryset


class RecipeView(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    # permission_classes = [IsAuthorOrReadOnly, ]
    permissions = [IsAuthenticatedOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    # filter_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        user = self.request.user
        tags = self.request.query_params.getlist('tags')
        queryset = models.Recipe.objects.all()

        if is_favorited and is_favorited == "1":
            if user.is_authenticated:
                queryset = models.Recipe.objects.filter(favorite__user=user)

        # Фильтруем рецепты по выбранным тегам
        if tags:
            #  это специальное выражение для фильтрации через связанные поля
            tag_filter = Q(tags__slug__in=tags)
            # distinct() для получения уникальных записей
            queryset = queryset.filter(tag_filter).distinct()

        return queryset

    """Данная функция позволяет определить какой сериализатор следует использовать в зависимости от HTTP запроса"""

    def get_serializer_class(self):
        method = self.request.method
        if method == "POST" or method == "PATCH":
            return serializers.CreateRecipeSerializers
        return serializers.ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class FavoriteView(APIView):
    permission_classes = [IsAuthorOrReadOnly, ]

    @action(methods=["post", ], detail=True, )
    def post(self, request, recipe_id):
        user = request.user
        data = {"user": user.id, "recipe": recipe_id, }
        """Проверка, состоит ли объект модели в избранном для данного user и рецепта"""
        if models.Favorite.objects.filter(user=user, recipe_id=recipe_id).exists():
            return Response({"Ошибка": "Вы уже добавили в избранное"}, status=status.HTTP_400_BAD_REQUEST, )
        serializer = serializers.FavoriteSerializers(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["DELETE", ], detail=True, )
    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(models.Recipe, id=recipe_id)
        if not models.Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        models.Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None

    @action(methods=["post", ], detail=True)
    def post(self, request, recipe_id):
        user = request.user
        data = {"user": user.id, "recipe": recipe_id, }
        if models.ShoppingCart.objects.filter(user=user, recipe_id=recipe_id).exists():
            return Response({"Ошибка": "Вы уже добавили в корзину"}, status=status.HTTP_400_BAD_REQUEST, )
        serializer = serializers.ShoppingCartSerializers(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["DELETE", ], detail=True)
    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(models.Recipe, id=recipe_id)
        if not models.ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        models.ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):

    def get(self, request):
        user = request.user
        shopping_cart = user.shopping_cart.all()
        buying_list = {}
        for record in shopping_cart:
            # для каждой записи получает связанный с ней рецепт
            recipe = record.recipe
            ingredients = models.IngredientInRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in buying_list:
                    buying_list[name] = {
                        "measurement_unit": measurement_unit,
                        "amount": amount,
                    }
                else:
                    buying_list[name]["amount"] = (
                            buying_list[name]["amount"] + amount
                    )
        wishlist = []
        for name, data in buying_list.items():
            wishlist.append(
                f"{name} - {data['amount']} {data['measurement_unit']}"
            )
        response = HttpResponse(wishlist, content_type="text/plain")
        return response
