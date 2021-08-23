from django.db import models

from foodgram import settings
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        help_text='Укажите название тега'
    )
    color = models.CharField(
        verbose_name=u'Color',
        max_length=7,
        help_text=u'HEX color, as #RRGGBB',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги'
        ordering = ['id']


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Укажите единицу измерения'
    )

    class Meta:
        verbose_name = 'Игредиент',
        verbose_name_plural = 'Игредиенты'
        ordering = ['name']


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь подписчик')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь на которого подписываемся')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow')]

    def __str__(self):
        return f'{self.user} => {self.author}'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        through='TagRecipe',
        related_name='recipes',
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        help_text='Напишите название рецепта'
    )
    image = models.ImageField(
        upload_to='image/',
        verbose_name='Картинка рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Добавьте сюда описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Укажите Время приготовления в минутах',
        error_messages={'invalid': 'Убедитесь, что значение'
                                   ' больше либо равно 0'}
    )
    # pub_date = models.DateTimeField(
    #     'Дата публикации',
    #     auto_now_add=True
    # )

    class Meta:
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество игредиентов'
    )

    class Meta:
        verbose_name = 'Количество игредиентов',
        verbose_name_plural = 'Количества игредиентов'
        ordering = ['id']


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Теги в рецепте',
        verbose_name_plural = 'Теги в рецептах'
        ordering = ['id']


class ShoppingCart(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Покупатель'
    )
    item = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Товар'
    )

    class Meta:
        verbose_name = 'Список покупок',
        verbose_name_plural = 'Списки покупок'
        ordering = ['id']


class Favorite(models.Model):
    fav_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    fav_item = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранное',
        verbose_name_plural = 'Избранные'
        ordering = ['id']
