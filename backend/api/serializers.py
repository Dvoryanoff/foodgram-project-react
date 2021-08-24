from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag, TagRecipe)
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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagRecipe
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class ListRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagRecipeSerializer(
        source='tagrecipe_set',
        many=True,
        required=False
    )
    ingredients = RecipeIngredientSerializer(
        source='ingredientamount_set',
        many=True,
        required=False
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        fav_user = self.context.get("user_id")
        fav_item = obj.id
        return Favorite.objects.filter(
            fav_user=fav_user,
            fav_item=fav_item
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        owner = self.context.get("user_id")
        item = obj.id
        return ShoppingCart.objects.filter(owner=owner, item=item).exists()


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagRecipeSerializer(
        source='tagrecipe_set',
        many=True,
        required=False
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredientamount_set',
        many=True,
        required=False
    )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def validate(self, data):
        unique_ingr = data['ingredients']
        ingr_list = []
        for item in unique_ingr:
            id = item['id']
            amount = item['amount']
            try:
                exist_item = get_object_or_404(
                    IngredientAmount, id=id, amount=amount
                )
                if exist_item.ingredient in ingr_list:
                    raise serializers.ValidationError(
                        {
                            'message': 'Извините,'
                            ' но добавить одинаковые ингредиенты нельзя.'
                        }
                    )
                else:
                    ingr_list.append(exist_item.ingredient)
            except Exception:
                new_ingr = get_object_or_404(Ingredient, id=id)
                if new_ingr in ingr_list:
                    raise serializers.ValidationError(
                        {
                            'message': 'Извините,'
                            ' но добавить одинаковые ингредиенты нельзя.'
                        }
                    )
                else:
                    ingr_list.append(new_ingr)

        if len(ingr_list) != len(set(ingr_list)):
            raise serializers.ValidationError(
                {
                    'message': 'Извините,'
                    ' но добавить одинаковые ингредиенты нельзя.'
                }
            )
        return data

    def create(self, validated_data):
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")

        request = self.context.get("request")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(
            image=image, author=request.user, **validated_data
        )
        for tag in tags:
            recipe.tags.add(tag)

        items = [
            IngredientAmount(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=item["id"]),
                amount=item["amount"],
            )
            for item in ingredients
        ]

        IngredientAmount.objects.bulk_create(items)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        try:
            image = validated_data.pop("image")
            instance.image = image
            instance.save()
        except KeyError:
            pass

        recipe = Recipe.objects.filter(id=instance.id)
        recipe.update(**validated_data)

        instance_tags = [tag for tag in instance.tags.all()]

        for tag in tags:
            if tag in instance_tags:
                instance_tags.remove(tag)
            else:
                instance.tags.add(tag)
        instance.tags.remove(*instance_tags)

        instance_ingredients = [
            ingredient for ingredient in instance.ingredients.all()
        ]
        for item in ingredients:
            amount = item["amount"]
            id = item["id"]
            try:
                exist_item_ingredient = IngredientAmount.objects.get(
                    id=id, amount=amount
                )

                instance_ingredients.remove(exist_item_ingredient.ingredient)
            except IngredientAmount.DoesNotExist:
                IngredientAmount.objects.create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient, id=id),
                    amount=amount,
                )

        instance.ingredients.remove(*instance_ingredients)

        return instance


class ShoppingCartCreateSerializer(serializers.ModelSerializer):
    item = serializers.IntegerField(source='item.id')
    owner = serializers.IntegerField(source='owner.id')

    class Meta:
        model = ShoppingCart
        fields = ['item', 'owner']

    def create(self, validated_data):
        item = get_object_or_404(
            Recipe,
            pk=validated_data.get('item').get('id')
        )
        owner = validated_data.get('owner')
        return ShoppingCart.objects.create(item=item, owner=owner)

    def validate(self, data):
        if ShoppingCart.objects.filter(
                item__id=data.get('item').get('id'),
                owner__id=data.get('owner').get('id')).exists():
            raise serializers.ValidationError(
                'Вы уже добавили в список покупок'
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='fav_item.id')
    name = serializers.ReadOnlyField(source='fav_item.name')
    image = Base64ImageField(read_only=True, source='fav_item.image')
    cooking_time = serializers.ReadOnlyField(source='fav_item.cooking_time')

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteCreateSerializer(serializers.ModelSerializer):
    fav_item = serializers.IntegerField(source='fav_item.id')
    fav_user = serializers.IntegerField(source='fav_user.id')

    class Meta:
        model = Favorite
        fields = ['fav_item', 'fav_user']

    def create(self, validated_data):
        fav_item = get_object_or_404(
            Recipe,
            pk=validated_data.get('fav_item').get('id')
        )
        fav_user = validated_data.get('fav_user')
        return Favorite.objects.create(fav_item=fav_item, fav_user=fav_user)

    def validate(self, data):
        if Favorite.objects.filter(
                fav_item__id=data.get('fav_item').get('id'),
                fav_user__id=data.get('fav_user').get('id')).exists():
            raise serializers.ValidationError(
                'Вы уже добавили в избранное'
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='item.id')
    name = serializers.ReadOnlyField(source='item.name')
    image = Base64ImageField(read_only=True, source='item.image')
    cooking_time = serializers.ReadOnlyField(source='item.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']
