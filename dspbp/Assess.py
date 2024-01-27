#	dspbptk - Dyson Sphere Program Blueprint Toolkit
#	Copyright (C) 2024 Alan Ray
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

import collections
import math
import os

from .Utils import maybeDysonSphereItem, maybeRecipe
from .Enums import DysonSphereItem as dsi, LogisticsStationDirection, ProductCategory
from .Recipes import ItemProduction, RECIPE_MAP, Machine, PRODUCT_CATEGORY_MAP

Sector = collections.namedtuple("Sector", ['name', 'abbreviation', 'height', 'width'])

class Assessment:
	def __init__(self, blueprint):
		self.decoded_data = blueprint.decoded_data
		self.size_assessment = SizeAssessment(self.decoded_data)

		# Eventually, some of this probably should fit into separate blueprints
		building_counter = collections.Counter()
		recipe_counter = collections.Counter()
		building_recipe_counter = collections.Counter()
		self.building_counter = building_counter
		self.recipe_counter = recipe_counter
		self.building_recipe_counter = building_recipe_counter

		# We have two types of inputs and outputs: Defined inputs/outputs (e.g. via stations or distributors)
		# and observed inputs/outputs -- production that is never used elsewhere or recipe requirements that
		# aren't constructed.
		#
		# For now, mostly rely on observed behavior. Proliferation is the exception, since we can't tell what
		# is/isn't being proliferated. If proliferation is available, the final production step is assumed
		# to be proliferated. Proliferation is assumed to be additional product, not speedup.
		# Aside from outputs, internal production / consumption is assumed to be balanced.
		#
		# This won't work quite right for complex blueprints (e.g. those that overflow outputs of intermediate steps)
		# but vastly simplifies calculations. There are obviously a lot of improvements possible, such as:
		# - More accurately assessing intermediate steps and which machines should be upgraded
		# - Determining which steps are proliferated
		# - Validating known inputs/outputs match actual inputs / outputs
		inputs = ItemProduction()
		outputs = ItemProduction()

		self.imports = set([])
		self.exports = set([])

		for building in self.decoded_data.buildings:
			item_type = maybeDysonSphereItem(building.data.item_id) or f'[{building.data.item_id}]'
			building_counter[item_type] += 1
			if building.data.recipe_id:
				recipe_id = maybeRecipe(building.data.recipe_id)
				if  recipe_id:
					building_recipe_counter[(building.data.item_id, building.data.recipe_id)] += 1
					recipe_counter[recipe_id] += 1
				else:
					print(f'Unknown recipe id {building.data.recipe_id}')

			if item_type in [dsi.PlanetaryLogisticsStation, dsi.InterstellarLogisticsStation]:
				for storage in building.parameters.storage:
					if not storage:
						continue
					if not storage['item_id']:
						continue
					storage_id = maybeDysonSphereItem(storage['item_id'])
					if not storage_id:
						print(f'Unknown storage id {storage['item_id']}')
						storage_id = f'u{storage['item_id']}'
					if item_type == dsi.InterstellarLogisticsStation and LogisticsStationDirection.Input == storage['remote_logic']:
						self.imports.add(storage_id)
					elif LogisticsStationDirection.Input == storage['local_logic']:
						self.imports.add(storage_id)
					if item_type == dsi.InterstellarLogisticsStation and LogisticsStationDirection.Output == storage['remote_logic']:
						self.exports.add(storage_id)
					elif LogisticsStationDirection.Output == storage['local_logic']:
						self.exports.add(storage_id)
			elif item_type == dsi.LogisticsDistributor:
				if building.data.filter_id:
					item_id = maybeDysonSphereItem(building.data.filter_id or f'u{building.data.filter_id}')
					if building.parameters.parameters.supply_logic == LogisticsStationDirection.Input:
						self.imports.add(item_id)
					elif building.parameters.parameters.supply_logic == LogisticsStationDirection.Output:
						self.exports.add(item_id)

		self.proliferate = dsi.ProliferatorMkIII if dsi.ProliferatorMkIII in self.imports \
			else dsi.ProliferatorMkII if dsi.ProliferatorMkII in self.imports \
			else dsi.ProliferatorMkI if dsi.ProliferatorMkI in self.imports \
			else None

		for ((item_type_id, recipe_id), amount) in building_recipe_counter.most_common():
			recipe = None if recipe_id == 0 else (maybeRecipe(recipe_id) or f'[{recipe_id} (recipe)]')
			item_type = maybeDysonSphereItem(item_type_id) or f'[{building.data.item_id}]'
			if recipe_id:
				if recipe_id in RECIPE_MAP:
					recipe_production = RECIPE_MAP[recipe_id]
					inputs -= ItemProduction(recipe_production.calculate_inputs({ item_type : amount }))
					outputs += ItemProduction(recipe_production.calculate_outputs({ item_type : amount }, self.proliferate))
				else:
					print(f'\tRecipe {recipe.name} has no production information')

		self.intermediate_inputs = {}
		self.intermediate_outputs = {}
		self.inputs = {}
		self.outputs = {}

		for item, amount in inputs.items():
			if item in outputs._items.keys():
				self.intermediate_inputs[item] = -amount
			else:
				self.inputs[item] = -amount
		for item, amount in outputs.items():
			if item in inputs._items.keys():
				self.intermediate_outputs[item] = amount
			else:
				self.outputs[item] = amount

		self.primary_output_id, self.primary_output_amount = ItemProduction(self.outputs).primary_output
		self.primary_output_id = maybeDysonSphereItem(self.primary_output_id) or self.primary_output_id
	@property
	def tech_level(self):
		return max(Machine.registry[item_id].tech_level if item_id in Machine.registry else 0 for item_id in self.building_counter)


class SizeAssessment:
	# +1 on sectors allows blueprints that exactly fit the height
	SECTORS = [
		# Technically, some tertiary sectors are 30 wide instead, but keep this simple
		Sector('tiny', 't', 10, 25),
		Sector('tertiary', 'C', 2.5 * 10 + 1, 2.5 * 10),
		Sector('secondary', 'B', 5 * 10 + 1, 4 * 10),
		Sector('equator', 'A', 8 * 10 + 1, 5 * 10),
		# Planetary dimensions are special:
		# - Height should be small so nothing fits by accident
		# - Width should be small so that no more than 1 blueprint "fits"
		Sector('planetary', 'P', 0, 1),  # Also default sector size
	]

	def __init__(self, blueprint_decoded_data):
		self.areas = blueprint_decoded_data._areas

		if len(self.areas) > 1:
			# Some debugging
			print(f'Warning: multi-area blueprints are not yet handled by {self.__class__}')
			print(f'    Found {len(self.areas)} areas...')
			for area in self.areas:
				print(f'   {area}')

	def _height_scale(self):
		primary_area = self.areas[0]
		chosen_sector = None
		for sector in self.SECTORS:
			if primary_area._fields.height <= sector.height:
				return sector
		return self.SECTORS[-1]

	@property
	def height_scale(self):
		return self._height_scale().abbreviation

	@property
	def sector_widths(self):
		primary_area = self.areas[0]
		sector = self._height_scale()
		return math.ceil(primary_area._fields.width / sector.width)

	def __str__(self):
		primary_area = self.areas[0]
		s = []
		height = primary_area._fields.height
		width = primary_area._fields.width
		for sector in self.SECTORS:
			if height <= sector.height:
				multiple = math.floor(sector.height/height)
				multiple_s = f'({multiple}x)' if multiple > 1 else ''
				s.append(f'{sector.name} {math.ceil(width/sector.width)} wide {multiple_s}')
		if not s:
			sector = self.SECTORS[-1]
			s.append(f'{sector.name}')

		return f'placement: {', '.join(s)}  -- ({width}x{height})'


def derive_destination_folder(filename, assessment):
	folder = os.path.dirname(filename) if os.path.isfile(filename) else filename
	blueprint_root, sep, _ = folder.partition('Blueprint')
	blueprint_root = blueprint_root + sep
	category = PRODUCT_CATEGORY_MAP.get(assessment.primary_output_id)

	# Don't move things that don't produce known items.
	if not category:
		return folder

	# Science always goes in the same folder
	if category == ProductCategory.ScienceMatrix:
		return os.path.join(blueprint_root,category.value, f'{category.value} - {assessment.primary_output_id.name}')

	# Any product production without a PLS/ILS and a low tech level is probably an early game aide.
	if dsi.PlanetaryLogisticsStation not in assessment.building_counter \
		and dsi.InterstellarLogisticsStation not in assessment.building_counter \
		and assessment.tech_level <= 3:
		return os.path.join(blueprint_root, 'Bootstrap')

	return os.path.join(blueprint_root, category.value)
