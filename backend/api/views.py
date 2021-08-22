import io
from typing import Union

from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.models import CustomUser

from .filterset import IngredientFilter, RecipeFilter
from .permissions import IsAdmin, IsAuthorOrAdmin, IsSuperuser
from .serializers import (FavoriteCreateSerializer, FavoriteSerializer,
                          FollowCreateSerializer, FollowSerializer,
                          IngredientSerializer, ListRecipeSerializer,
                          RecipeSerializer, ShoppingCartCreateSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)

BASE_USERNAME = 'User'


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated,
                          Union[IsSuperuser, IsAdmin],)

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


class SubscribeView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        user = self.request.user
        serializer = FollowCreateSerializer(
            data={'user': user.id, 'author': user_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        follow = get_object_or_404(Follow, user=user, author_id=user_id)
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        follow = get_object_or_404(Follow, user=user, author_id=user_id)
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = PageNumberPagination
    serializer = FollowSerializer(pagination_class, many=True)

    def get_queryset(self, *args, **kwargs):
        return Follow.objects.filter(followers__user=self.request.user)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        subscriptions = Follow.objects.filter(user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class FavoriteViewSet(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FavoriteSerializer
    pagination_class = None

    def get(self, request, recipe_id):
        fav_user = self.request.user
        serializer = FavoriteCreateSerializer(
            data={'fav_item': recipe_id, 'fav_user': fav_user.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(fav_user=self.request.user)
        shopcart = get_object_or_404(
            Favorite,
            fav_item_id=recipe_id,
            fav_user=fav_user
        )
        serializer = FavoriteSerializer(shopcart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        fav_user = request.user
        follow = get_object_or_404(
            Favorite,
            fav_item_id=recipe_id,
            fav_user=fav_user
        )
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TagSerializer
    pagination_class = None

    def get(self, request, recipe_id):
        owner = self.request.user
        serializer = ShoppingCartCreateSerializer(
            data={'item': recipe_id, 'owner': owner.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        shopcart = get_object_or_404(
            ShoppingCart, item_id=recipe_id, owner=owner)
        serializer = ShoppingCartSerializer(shopcart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        follow = get_object_or_404(
            ShoppingCart, item_id=recipe_id, owner=user)
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = ListRecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user_id": self.request.user.id})
        return context

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', ])
    def download_shopping_cart(self, request):
        buffer = io.BytesIO()
        cnvs = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
        pdfmetrics.registerFont(TTFont(
            'FreeSans',
            settings.STATIC_ROOT + '/FreeSans.ttf')
        )
        textob = cnvs.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("FreeSans", 14)

        user = request.user
        recipes_id = ShoppingCart.objects.filter(owner=user).values('item')
        ingredients_id = Recipe.objects.filter(
            id__in=recipes_id
        ).values('ingredients')
        ingredients = Ingredient.objects.filter(id__in=ingredients_id)

        lines = []

        for ingredient in ingredients:
            amount = IngredientAmount.objects.filter(
                ingredient=ingredient,
                recipe__in=recipes_id
            ).aggregate(total_amount=Sum('amount'))["total_amount"]

            lines.append(ingredient.name)
            lines.append(str(amount))
            lines.append(" ")
            lines.append(
                f'''{ingredient.name} ({ingredient.measurement_unit})
                 – {str(amount)}'''
            )

        for line in lines:
            textob.textLine(line)

        cnvs.drawText(textob)
        cnvs.showPage()
        cnvs.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename='shop.pdf')

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['tags'] = [{'id': idx} for idx in data['tags']]
        serializer = RecipeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        instance.id = pk
        instance.save()
        data = request.data.copy()
        data['tags'] = [{'id': idx} for idx in data['tags']]
        serializer = RecipeSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
