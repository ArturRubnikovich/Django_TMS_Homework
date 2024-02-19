"""
URL configuration for lesson20 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import serve
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from posts import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('accounts/register', views.register, name="register"),
    path("register/confirm/<uidb64>/<token>", views.confirm_register_view, name="register-confirm"),
    path("register/", views.register_view, name="register"),
    path("reset/confirm/<uidb64>/<token>", views.confirm_reset_view, name="reset-confirm"),
    path("reset/", views.reset_view, name="reset"),
    path("", views.home_page_view, name="home"),
    path("filter", views.filter_notes_view, name="filter-notes"),
    path("create", views.create_note_view, name="create-note"),
    path("post/<note_uuid>", views.show_note_view, name="show-note"),
    path("about", views.show_about_us_view, name="about_us"),
    path("edit/<note_uuid>", views.edit_note_view, name="edit-note"),
    path("post/<note_uuid>/delete", views.delete_note_view, name="delete-note"),
    path("user/<username>/posts", views.user_posts, name="user-posts"),
    path("profile/<username>", views.user_profile, name="user-profile"),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("__debug__/", include("debug_toolbar.urls")),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("api/", include("posts.api.urls")),
    # Token
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api/auth/", include("djoser.urls.jwt")),
    path("api/auth/", include("djoser.urls.base")),
    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('history', views.ListHistoryOfPages.as_view(), name='show-history-of-pages'),
]
