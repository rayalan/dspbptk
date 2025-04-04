#	dspbptk - Dyson Sphere Program Blueprint Toolkit
#	Copyright (C) 2023 Alan Ray
#
#	This file is part of dspbptk.
#
#	dspbptk is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	dspbptk is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
import json
import collections
import math
import os

from BaseAction import BaseAction
from dspbp.Blueprint import Blueprint
from dspbp.Enums import DysonSphereItem as dsi
from dspbp.Utils import maybeDysonSphereItem, maybeRecipe
from dspbp.Recipes import ItemProduction, RECIPE_MAP, Machine

def calculate_area(areas):
	EQUATOR_SECTOR_HEIGHT = 8 * 10 + 1
	SECONDARY_SECTOR_HEIGHT = 5 * 10 + 1
	TERTIARY_SECTOR_HEIGHT = 2.5 * 10 + 1
	EQUATOR_SECTOR_WIDTH = 5 * 10
	SECONDARY_SECTOR_WIDTH = 4 * 10
	TERTIARY_SECTOR_WIDTH = 2.5 * 10 # Technically, some tertiary sectors are 30 wide instead

	if len(areas) > 1:
		return 'unknown (multiarea blueprint)'
	primary_area = areas[0]
	width = primary_area._fields.width
	height = primary_area._fields.height

	# Blueprints with exact heights are intend to match one location
	can_be_equator = height <= EQUATOR_SECTOR_HEIGHT
	can_be_secondary = height <= SECONDARY_SECTOR_HEIGHT
	can_be_tertiary = height <= TERTIARY_SECTOR_HEIGHT

	s = []
	if not can_be_equator and not can_be_secondary and not can_be_tertiary:
		s.append('planetary (special)')
	if can_be_equator:
		multiple = math.floor(EQUATOR_SECTOR_HEIGHT/height)
		multiple_s = f'({multiple}x)' if multiple > 1 else ''
		s.append(f'equator {math.ceil(width/EQUATOR_SECTOR_WIDTH)} wide {multiple_s}')
	if can_be_secondary:
		multiple = math.floor(SECONDARY_SECTOR_HEIGHT/height)
		multiple_s = f'({multiple}x)' if multiple > 1 else ''
		s.append(f'secondary {math.ceil(width/SECONDARY_SECTOR_WIDTH)} wide {multiple_s}')
	if can_be_tertiary:
		multiple = math.floor(TERTIARY_SECTOR_HEIGHT/height)
		multiple_s = f'({multiple}x)' if multiple > 1 else ''
		s.append(f'tertiary {math.ceil(width/TERTIARY_SECTOR_WIDTH)} wide {multiple_s}')
	return f'placement{'s' if len(s) > 1 else ''} ({width}x{height}): ' + ', '.join(s)

class ActionInspect(BaseAction):
	def run(self):
		# input_files = self.find_blueprints(self._args.inputs)
		for filename, bp in self.blueprints(self._args.inputs): # , self._args.verbose, self._args.ignore_corrupt):
		# for input_file in input_files:
			print(f'Blueprint source: {filename}')
			building_counter = collections.Counter()

			# bp = Blueprint.read_from_file(input_file, validate_hash = not self._args.ignore_corrupt)
			bpd = bp.decoded_data

			bp_dict = bp.to_dict()
			# print(json.dumps(bp_dict, indent = 4, sort_keys = True))

			inputs = ItemProduction()
			outputs = ItemProduction()
			known_transfers = []
			max_outputs = ItemProduction()

			unique_buildings = set()
			unique_recipes = set()

			for building in bpd.buildings:
				item_type = maybeDysonSphereItem(building.data.item_id) or f'[{building.data.item_id}]'
				if building.data.recipe_id:
					building_counter[(building.data.item_id, building.data.recipe_id)] += 1
					unique_recipes.add(building.data.recipe_id)
				unique_buildings.add(building.data.item_id)

				if item_type in [dsi.PlanetaryLogisticsStation, dsi.InterstellarLogisticsStation]:
					for storage in building.parameters.storage:
						if not storage:
							continue
						known_transfers.append(maybeDysonSphereItem(storage['item_id'] or f'u{storage['item_id']}'))
				elif item_type == dsi.LogisticsDistributor:
					known_transfers.append(maybeDysonSphereItem(building.data.filter_id or f'u{building.data.filter_id}'))

			proliferate = dsi.ProliferatorMkIII if dsi.ProliferatorMkIII in known_transfers \
				else dsi.ProliferatorMkII if dsi.ProliferatorMkII in known_transfers \
				else dsi.ProliferatorMkI if dsi.ProliferatorMkI in known_transfers \
				else None

			for ((item_type_id, recipe_id), amount) in building_counter.most_common():
				recipe = None if recipe_id == 0 else (maybeRecipe(recipe_id) or f'[{recipe_id} (recipe)]')
				item_type = maybeDysonSphereItem(item_type_id) or f'[{building.data.item_id}]'

				print("%5d  %s %s (%s)" % (amount, item_type.name, getattr(recipe, 'name', recipe), recipe))
				if recipe_id:
					if recipe_id in RECIPE_MAP:
						recipe_production = RECIPE_MAP[recipe_id]
						# Improve: Figure out if there should be input proliferation
						inputs += ItemProduction(recipe_production.calculate_inputs({ item_type : amount }, None))
						outputs += ItemProduction(recipe_production.calculate_outputs({ item_type : amount }, proliferate))
						max_outputs += ItemProduction(recipe_production.calculate_outputs({ Machine.registry[item_type].find_tech_level_equivalent_machine(10) : amount }, dsi.ProliferatorMkIII))
					else:
						print(f'\tRecipe {recipe.name} has no production information')

			print(f'Unique building types: {len(unique_buildings)}, unique recipies: {len(unique_recipes)}')
			tech_level = max(Machine.registry[item_id].tech_level if item_id in Machine.registry else 0 for item_id in unique_buildings)
			print(f'Tech level: {tech_level}')
			# Let's assume that usually we're only interested in net inputs/outputs, and everything else can be ignored
			# print(outputs)
			area_s = calculate_area(bpd._areas)

			print(f'Area: {area_s}')

			net_outputs = outputs - inputs
			if not self._args.full:
				for item in (outputs - inputs)._items:
					if item in inputs._items and item in outputs._items:
						del net_outputs._items[item]
						del max_outputs._items[item]
			print('Input/output summary')
			print(net_outputs)
			primary_output_id, primary_output_amount = net_outputs.primary_output
			print(f'Primary output: { primary_output_id.name if primary_output_id else 'None'} @ {round(primary_output_amount,1)}/sec')

			folder = os.path.dirname(filename)
			blueprint_root, sep, _ = folder.partition('Blueprint')
			blueprint_root = blueprint_root + sep
			if primary_output_id in [
				dsi.ElectromagneticMatrix, dsi.EnergyMatrix, dsi.StructureMatrix, dsi.InformationMatrix, dsi.GravityMatrix,
			    dsi.UniverseMatrix]:
				folder = os.path.join(blueprint_root,f'Science/Science - {primary_output_id.name}')
			elif primary_output_id in [
				dsi.StoneBrick, dsi.Glass, dsi.IronIngot, dsi.Magnet, dsi.CopperIngot, dsi.TitaniumIngot,
				dsi.TitaniumAlloy, dsi.CrystalSilicon, dsi.HighPuritySilicon, dsi.EnergeticGraphite, dsi.Diamond,
				]:
				folder = os.path.join(blueprint_root,'Smelters')
			else:
				folder = os.path.join(blueprint_root,'Intermediate Products')
			print(f'Folder: {folder}')

			# Filename is: [PrimaryOutput] [TechLevel][Scale][Width][i]-[RecipeCount][+?] [Quantity]
			# where
			#   - one `i` is used for each advanced recipe used
			#   - '+' is used if proliferation is used
			#   - Tech level is 1 to 7 in Roman numerals
			#   - Scale is P (planetary), A, B, or C depending on where the blueprint fits
			#   - Width is the number of sectors wide the blueprint is
			#
			# The overall goal is to make it easy to have unique blueprint names that can be leveled up/down

			# Short description matches filename

			# Proposed icons
			# Proposed description
			print()

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			parser.add_argument("--ignore-corrupt", action = "store_true", help = "Do not validate the checksum when reading the blueprint file.")
			parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity.")
			parser.add_argument("-f", "--full", action="store_true", help="Calculate deltas for internal production rates, not just inputs/outputs")
			parser.add_argument("inputs", nargs = "+", help = "Input blueprint file(s) and/or directory(s)")
		multicommand.register("inspect", "Inspect blueprints", genparser, action = cls)
