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
import os

from BaseAction import BaseAction
from dspbp.Blueprint import Blueprint
from dspbp.Enums import DysonSphereItem, Recipe

def maybeDysonSphereItem(id_):
	try:
		return DysonSphereItem(id_)
	except ValueError:
		return None

def maybeRecipe(id_):
	try:
		return Recipe(id_)
	except ValueError:
		return None

class ActionSearchUnknownIds(BaseAction):
	def run(self):

		input_files = self.find_blueprints(self._args.inputs)

		new_ids = {}

		for blueprint_file in input_files:
			if blueprint_file == '_intro_':
				continue
			bp = Blueprint.read_from_file(blueprint_file, validate_hash = not self._args.ignore_corrupt)
			bpd = bp.decoded_data

			building_counter = collections.Counter()
			for building in bpd.buildings:
				building_counter[building.data.item_id] += 1
				if building.data.recipe_id:
					# print(building.data.recipe_id)
					if not maybeRecipe(building.data.recipe_id):
						name = f'{building.data.recipe_id} (recipe)'
						if name not in new_ids:
							new_ids[name] = set([])
						new_ids[name].add(blueprint_file)


			for (item_id, count) in building_counter.most_common():
				try:
					item = DysonSphereItem(item_id)
				except ValueError:
					if item_id not in new_ids:
						new_ids[item_id] = set([])
					new_ids[item_id].add(blueprint_file)

		if len(new_ids):
			print(f'New ids ({len(new_ids)} entries):')
		else:
			print('No new ids found')
		for item, blueprints in new_ids.items():
			print(f'\t{item}: {', '.join(blueprints)}')

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			parser.add_argument("--ignore-corrupt", action = "store_true", help = "Do not validate the checksum when reading the blueprint file.")
			parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity.")
			parser.add_argument("inputs", nargs = "+", help = "Input blueprint file(s) and/or directory(s)")
		multicommand.register("search-new-ids", "Search all blueprints for unknown ids", genparser, action = cls)
