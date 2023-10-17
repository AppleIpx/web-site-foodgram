from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserView

router = DefaultRouter()
router.register("users", UserView)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path("", include(router.urls)),
]
