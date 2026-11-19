from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("bookstore.urls")),
    path("api/v1/auth/jwt/create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("api/v1/auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("api/v1/auth/jwt/logout/", TokenBlacklistView.as_view(), name="jwt-logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
