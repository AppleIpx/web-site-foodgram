from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserView

router = DefaultRouter()
router.register("users", UserView)

urlpatterns = [
    # path('api/create/', UserCreateView.as_view()),
    # path('all/', AllUsersInfoView.as_view()),
    # path('detail/<int:pk>', InfoAoutUserView.as_view(),),
    # path('api/auth/', include('djoser.urls')), #api/auth/users/ регистрация
    path('auth/', include('djoser.urls.authtoken')), #api/auth/users/ регистрация
    path("", include(router.urls)),
    # re_path(r'^auth/', include('djoser.urls.authtoken')), #auth/token/login/ токен
]


