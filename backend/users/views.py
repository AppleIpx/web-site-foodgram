from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .serializers import *
from .models import User, Follow
from rest_framework.permissions import IsAuthenticated, AllowAny


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )
    pagination_class = None

    @action(methods=["get"], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(["post"], detail=False, permission_classes=(IsAuthenticated, ))
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_password = request.data.get("new_password")
            current_password = request.data.get("current_password")
            if user.check_password(current_password):
                if new_password == current_password:
                    raise serializers.ValidationError({'new_password': 'Новый пароль должен отличаться от текущего.'})
                user.set_password(new_password)
                user.save()
                return Response({"status": "password set"})
            else:
                raise serializers.ValidationError({'current_password': 'Неправильный пароль.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """detail=True - что действие будут применено для конкретного объекта
    following - человек на которого хотят подписаться
    follow - проверка связи между подписчиком и человека на которого
    хотят подписаться"""

    @action(["get", "delete", "post"], detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        user = request.user
        following = get_object_or_404(User, pk=pk)
        follow = Follow.objects.filter(user=user, following=following)
        data = {"user": user.id,
                "following": following.id, }
        if request.method == "GET" or request.method == "POST":
            if follow.exists():
                return Response("Вы уже подписаны", status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowerSerializer(data=data, context=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            follow.delete()
            return Response("Удаление прошло успешно", status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get", "post", ], detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        follow = Follow.objects.filter(user=user)
        user_obj = []
        for follow_obj in follow:
            user_obj.append(follow_obj.following)
        paginator = PageNumberPagination()
        paginator.page_size = 6
        result_page = paginator.paginate_queryset(user_obj, request)
        serializer = ShowFollowerSerializer(result_page, many=True,
                                            context={"current_user": user})
        return paginator.get_paginated_response(serializer.data)

