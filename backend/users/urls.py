from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserView

router = DefaultRouter()
router.register("users", UserView)
# router.register(r"users", UserView, basename="users")

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')), #api/auth/users/ регистрация
    # path('users/<int:user_id>/', UserView.as_view()),
    path("", include(router.urls)),
]


