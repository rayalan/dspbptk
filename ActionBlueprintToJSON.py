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

import os
import json
from BaseAction import BaseAction
from Blueprint import Blueprint

class ActionBlueprintToJSON(BaseAction):
	def run(self):
		if (not self._args.force) and os.path.exists(self._args.outfile):
			print("Refusing to overwrite: %s" % (self._args.outfile))
			return 1

		bp = Blueprint.read_from_file(self._args.infile, validate_hash = not self._args.ignore_corrupt)
		bp_dict = bp.to_dict()

		with open(self._args.outfile, "w") as f:
			if self._args.pretty_print:
				json.dump(bp_dict, f, indent = 4, sort_keys = True)
				f.write("\n")
			else:
				json.dump(bp_dict, f)

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			parser.add_argument("-f", "--force", action = "store_true", help = "Overwrite output file if it exists.")
			parser.add_argument("-p", "--pretty-print", action = "store_true", help = "Create a pretty-printed output JSON file.")
			parser.add_argument("--ignore-corrupt", action = "store_true", help = "Do not validate the checksum when reading the blueprint file.")
			parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity.")
			parser.add_argument("infile", help = "Input blueprint text file")
			parser.add_argument("outfile", help = "Output JSON file")
		multicommand.register("bp2json", "Convert a blueprint to JSON", genparser, action = ActionBlueprintToJSON)
