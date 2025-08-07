from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserDestroyAPIView, UserListAPIView, UserRetrieveAPIView, UserUpdateAPIView

app_name = UsersConfig.name


urlpatterns = [
    # Аутентификация и авторизация
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # CRUD для пользователей
    path('', UserListAPIView.as_view(), name='user-list'),
    path('<int:pk>/', UserRetrieveAPIView.as_view(), name='user-retrieve'),
    path('<int:pk>/edit/', UserUpdateAPIView.as_view(), name='user-update-admin'),
    path('<int:pk>/delete/', UserDestroyAPIView.as_view(), name='user-delete'),

    # Регистрация
    path('register/', UserCreateAPIView.as_view(), name='user-create'),
]
