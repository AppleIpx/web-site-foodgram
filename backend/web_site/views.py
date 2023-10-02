from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated

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
        if is_favorited and is_favorited == "1":
            if user.is_authenticated:
                # Фильтруем рецепты, которые добавлены в избранное текущим пользователем
                return models.Recipe.objects.filter(favorite__user=user)
        else:
            # Если пользователь анонимный, не отображаем ничего
            return models.Recipe.objects.all()

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

    @api_view(["GET", ])
    def download_shopping_cart(self, request):
        pass
