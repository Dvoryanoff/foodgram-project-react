from django.contrib.auth.models import User
from django.db import models
from foodgram import settings

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        blank=False,
        max_length=200,
        help_text='Укажите название ингредиента'
    )
    color = models.CharField(
        verbose_name=(u'Color'),
        max_length=7,
        help_text=(u'HEX color, as #RRGGBB'),
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
        blank=False,
        max_length=200,
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        blank=False,
        max_length=200,
        help_text='Укажите единицу измерения'
    )

    class Meta:
        verbose_name = 'Игредиент',
        verbose_name_plural = 'Игредиенты'
        ordering = ['id']




class Follow(models.Model):
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь подписчик')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь на которого подписываемся')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow')]

    def __str__(self):
        return f'{self.user} => {self.author}'
