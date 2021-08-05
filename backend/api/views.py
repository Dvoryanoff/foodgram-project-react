import io
from typing import Union

from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Follow
from users.models import CustomUser

from .permissions import IsAdmin, IsAuthorOrAdmin, IsSuperuser
from .serializers import (FollowCreateSerializer, FollowSerializer,
                          UserSerializer)

BASE_USERNAME = 'User'


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, Union[IsSuperuser, IsAdmin],)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', 'patch'],
        url_path='me')
    def get_or_update_self(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                instance=request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(
                request.user,
                many=False)
            return Response(serializer.data)

    def delete(self, request, recipe_id):
        fav_user = request.user
        fav_item = get_object_or_404(Recipe, pk=recipe_id)
        follow = get_object_or_404(
            Favorite,
            fav_item=fav_item,
            fav_user=fav_user
            )
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)


class SubscribeView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=user_id)
        serializer = FollowCreateSerializer(
            data={'user': user.id, 'author': user_id}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        follow = get_object_or_404(
            Follow,
            user=user,
            author=author
            )
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(CustomUser, id=user_id)
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user
        subscriptions = Follow.objects.filter(user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
