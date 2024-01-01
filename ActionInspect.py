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
from dspbp.Enums import DysonSphereItem

def maybeDysonSphereItem(id_):
	try:
		return DysonSphereItem(id_)
	except ValueError:
		return None

class ActionInspect(BaseAction):
	def run(self):
		input_files = []
		for input in self._args.inputs:
			if os.path.isfile(input):
				input_files.append(input)
			elif os.path.isdir(input):
				for root, dirs, files in os.walk(input):
					print(f'Searching {root}...')

					for blueprint_file in files:
						if blueprint_file == '_intro_':
							continue
						input_files.append(os.path.join(root, blueprint_file))
			else:
				raise ValueError(f'Unknown input {input}')

		for input_file in input_files:
			print(input)

			bp = Blueprint.read_from_file(input_file, validate_hash = not self._args.ignore_corrupt)
			bpd = bp.decoded_data

			for building in bpd.buildings:
				item_type = maybeDysonSphereItem(building.data.item_id)
				if item_type != DysonSphereItem.PlanetaryLogisticsStation and item_type != DysonSphereItem.InterstellarLogisticsStation:
					continue
				print(f'{item_type.name} ({building.data.item_id})')
				print(building.data)
				print(building, type(building))
				print()

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			parser.add_argument("--ignore-corrupt", action = "store_true", help = "Do not validate the checksum when reading the blueprint file.")
			parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity.")
			parser.add_argument("inputs", nargs = "+", help = "Input blueprint file(s) and/or directory(s)")
		multicommand.register("inspect", "Inspect blueprints", genparser, action = cls)
