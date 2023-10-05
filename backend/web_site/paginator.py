from rest_framework.pagination import PageNumberPagination

from . import models


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)

        # Изменить значение "count" на количество рецептов в списке покупок
        request = self.request
        if request and not request.user.is_anonymous:
            user = request.user
            shopping_cart_count = models.ShoppingCart.objects.filter(user=user).count()
            response.data['count'] = shopping_cart_count
        else:
            response.data['count'] = 0  # Если пользователь анонимный или отсутствует запрос

        return response