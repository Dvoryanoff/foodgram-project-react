from django.shortcuts import get_object_or_404
# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import Follow
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'id',
            'email',)
        model = CustomUser
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}}


class FollowCreateSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    author = serializers.IntegerField(source='author.id')

    class Meta:
        model = Follow
        fields = ['user', 'author']

    def create(self, validated_data):
        author = get_object_or_404(
            CustomUser,
            pk=validated_data.get('author').get('id')
            )
        user = validated_data.get('user')
        return Follow.objects.create(user=user, author=author)

    def validate(self, data):
        if Follow.objects.filter(
                author__id=data.get('author').get('id'),
                user__id=data.get('user').get('id')).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны'
                )
        return data


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            )

    def get_is_subscribed(self, obj):
        author = obj.author
        user = obj.user
        return Follow.objects.filter(author=user, user=author).exists()

    def get_recipes(self, obj):
        author = obj.author
        recepts_follow = Recipe.objects.filter(author=author)
        return RecipeSerializer(recepts_follow, many=True).data

    def get_recipes_count(self, obj):
        author = obj.author
        count = Recipe.objects.filter(author=author).count()
        return count
