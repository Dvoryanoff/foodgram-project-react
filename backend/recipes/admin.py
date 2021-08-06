from django.contrib import admin

from .models import Ingredient, Recipe, Tag

admin.site.register(Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'recipe_favorite_count'
        )
    search_fields = (
        'username',
        'email')
    list_filter = (
        'name',
        'author',
        'tags')

    def recipe_favorite_count(self, obj):
        return obj.favorite_set.count()

    recipe_favorite_count.short_description = "Число добавлений в избранное"


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        )
    list_filter = (
        'name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
