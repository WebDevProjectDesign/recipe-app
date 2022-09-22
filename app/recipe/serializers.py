from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """serializer for ingredient"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """serializer for recipes"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes',
                  'price', 'link', 'tags', 'ingredients', ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, create = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context['request'].user
        for item in ingredients:
            ing_obj, create = Ingredient.objects.get_or_create(
                user=auth_user,
                **item
            )
            recipe.ingredients.add(ing_obj)

    def create(self, data):
        """Creating recipe"""
        tags = data.pop('tags', [])
        ingredient = data.pop('ingredients', [])
        recipe = Recipe.objects.create(**data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredient, recipe)

        return recipe

    def update(self, instance, data):
        """Update recipe"""
        tags = data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailsSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
