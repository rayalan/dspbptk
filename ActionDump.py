#	dspbptk - Dyson Sphere Program Blueprint Toolkit
#	Copyright (C) 2021-2022 Johannes Bauer
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
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import json
import collections
from BaseAction import BaseAction
from dspbp.Blueprint import Blueprint
from dspbp.Enums import DysonSphereItem, Recipe
from dspbp.BlueprintData import ParameterType

class ActionDump(BaseAction):
	def run(self):
		for filename, bp in self.blueprints(self._args.inputs):
			if len(self._args.inputs) > 1:
				print(f"{filename}:")
			bpd = bp.decoded_data

			building_counter = collections.Counter()
			item_storage_counter = collections.Counter()
			for building in bpd.buildings:
				# IMPROVE: Why are we checking for conveyer sentinel when we're looking for storage? I suspect
				# this was an asleep at the switch mistake; revisit when there's a chance.
				# if building.parameters.SENTINEL == ParameterType.CONVEYOR and building.parameters.parameters:
				# 	item_storage_counter[(building.data.item_id, building.parameters.parameters.memo_icon)] += 1


				building_counter[(building.data.item_id, building.data.recipe_id)] += 1

			if bp.short_desc != "":
				print("Text          : %s" % (bp.short_desc))
			if bp.long_desc != "":
				print("Description   : %s\n" % (bp.long_desc))
			if self._args.verbose >= 1:
				print("Game version  : %s" % (bp.game_version))
			print("Building count: %d" % (len(bpd.buildings)))
			for ((item_id, recipe_id), count) in building_counter.most_common():
				try:
					item = DysonSphereItem(item_id)
					item_name = item.name
				except ValueError:
					item_name = f"[{item_id}]"
				print(f'{count:5} {item_name} {(Recipe(recipe_id).name if recipe_id in Recipe else 'Unknown'):20} ({recipe_id:3})')

			if item_storage_counter:
				print(f'\nStored items:')
			for ((container_id, item_id), count) in item_storage_counter.most_common():
				print(f'{count:5} {DysonSphereItem(container_id).name if container_id in DysonSphereItem else 'Unknown'} / {DysonSphereItem(item_id).name if item_id in DysonSphereItem else 'Unknown'} ({item_id:3})')


			if len(self._args.inputs) > 1:
				print()

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			cls._genparser(parser, is_folder_search=True)
		multicommand.register("dump", "Dump some information about blueprint(s)", genparser, action = cls)
