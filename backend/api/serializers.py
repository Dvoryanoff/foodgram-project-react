from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as BaseUserSerializer
from models import CustomUser, Follow, Ingredient
from rest_framework import serializers


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'
