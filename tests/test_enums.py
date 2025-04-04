import os

from dspbp.Blueprint import Blueprint
from dspbp import Enums

recipe_path = os.path.join('.', 'tests', 'blueprint', 'recipe_collection.txt')
# Items, not icons
item_path = os.path.join('.', 'tests', 'blueprint', 'item_collection.txt')

def test_recipes():
    bp = Blueprint.read_from_file(recipe_path)
    recipes = []
    for building in bp.decoded_data.buildings:
        assert building.data.recipe_id not in recipes
        assert building.data.recipe_id in Enums.Recipe
        recipes.append(building.data.recipe_id)
    for recipe in Enums.Recipe:
        # For now, we're missing one of these in our collection
        if recipe in [Enums.Recipe.DeuteriumFractionation, Enums.Recipe.ElectromagneticMatrix,
            Enums.Recipe.EnergyMatrix, Enums.Recipe.StructureMatrix, Enums.Recipe.InformationMatrix,
            Enums.Recipe.GravityMatrix, Enums.Recipe.UniverseMatrix]:
            continue
        assert recipe.value in recipes

def test_items():
    bp = Blueprint.read_from_file(item_path)
    items = []
    for building in bp.decoded_data.buildings:
        if not building.parameters.parameters:
            continue
        assert building.parameters.parameters.memo_icon not in items
        assert building.parameters.parameters.memo_icon in Enums.DysonSphereItem
        items.append(building.parameters.parameters.memo_icon)

    for item in Enums.DysonSphereItem:
        # For now, we're missing one of these in our collection
        assert item.value in items
