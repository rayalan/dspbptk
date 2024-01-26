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
from dspbp.Enums import DysonSphereItem

class ActionDump(BaseAction):
	def run(self):
		for filename in self._args.infile:
			if len(self._args.infile) > 1:
				print(f"{filename}:")
			bp = Blueprint.read_from_file(filename, validate_hash = not self._args.ignore_corrupt)
			bpd = bp.decoded_data

			building_counter = collections.Counter()
			for building in bpd.buildings:
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
				print("%5d  %s %s" % (count, item_name, recipe_id))
			if len(self._args.infile) > 1:
				print()
	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			parser.add_argument("--ignore-corrupt", action = "store_true", help = "Do not validate the checksum when reading the blueprint file.")
			parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity.")
			parser.add_argument("infile", nargs = "+", help = "Input blueprint text file(s)")
		multicommand.register("dump", "Dump some information about a blueprint", genparser, action = cls)
