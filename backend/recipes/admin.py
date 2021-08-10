from django.contrib import admin
from import_export.admin import ImportMixin

from .models import Ingredient, Recipe, Tag
from .resources import IngredientResource

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


# class IngredientAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'measurement_unit',
#     )
#     list_filter = (
#         'name',)


class IngredientAdmin(ImportMixin, admin.ModelAdmin):
    list_filter = ('name', 'measurement_unit',)
    search_fields = ('name',)
    resource_class = IngredientResource
    list_display = (
        'name',
        'measurement_unit',
    )


# admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
