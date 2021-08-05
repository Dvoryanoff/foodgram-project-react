from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubscribeListViewSet, SubscribeView, UsersViewSet

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeListViewSet.as_view({'get': 'list'}),
        name='subscriptions'
        ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls.jwt')),

    path(
        'users/<int:user_id>/subscribe/',
        SubscribeView.as_view(),
        name='follow'
        ),
]
