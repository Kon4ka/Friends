"""
URL configuration for friendtalk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from chat.views import RegisterUser, ProfileView, add_friend, FriendRequestListView, AcceptFriendRequestView, \
    OutRequestsView, decline_request_view, delete_friend, friend_request_status
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions #!

schema_view = get_schema_view(
   openapi.Info(
      title="Friends",
      default_version='v1',
      description="A simple API for my project",
      terms_of_service="https://github.com/Kon4ka/Friends",
      contact=openapi.Contact(email="lira0sirin@yandex.ru"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("register/", RegisterUser.as_view(), name="register"),
    path('add-friend/', add_friend, name='add_friend'),
    path('accounts/profile/', ProfileView.as_view(), name ='profile'),
    path('accounts/requests/', FriendRequestListView.as_view(), name='requests'),
    path('accounts/requests/accept/<int:q>/', AcceptFriendRequestView.as_view() , name='accept'),
    path('accounts/out-requests/', OutRequestsView.as_view(), name='out_requests'),
    path('accounts/requests/decline/<int:request_id>/', decline_request_view, name='decline_request'),
    path('accounts/delete/<int:friend_id>/', delete_friend, name='delete_friend'),
    path('accounts/<str:name>/', friend_request_status, name='status'),


]
