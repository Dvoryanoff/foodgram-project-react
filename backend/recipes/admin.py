from django.contrib import admin

from.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, Tag, PurchaseList,
    Subscribe
)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInLine]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInLine]


admin.site.register(Favorite)
admin.site.register(IngredientRecipe)
admin.site.register(PurchaseList)
admin.site.register(Subscribe)
admin.site.register(Tag)
