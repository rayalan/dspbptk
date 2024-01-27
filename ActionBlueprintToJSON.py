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
from dspbp.Blueprint import Blueprint

class ActionBlueprintToJSON(BaseAction):
	def run(self):
		if (not self._args.force) and self._args.outfile and os.path.exists(self._args.outfile):
			print("Refusing to overwrite: %s" % (self._args.outfile))
			return 1

		_, bp = next(self.blueprints([self._args.infile]))
		bp_dict = bp.to_dict()

		if self._args.outfile:
			with open(self._args.outfile, "w") as f:
				if self._args.pretty_print:
					json.dump(bp_dict, f, indent = 4, sort_keys = True)
					f.write("\n")
				else:
					json.dump(bp_dict, f)
		print(json.dumps(bp_dict, indent=4))

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			cls._genparser(parser, is_single_file=True)
			parser.add_argument("-f", "--force", action = "store_true", help = "Overwrite output file if it exists.")
			parser.add_argument("-p", "--pretty-print", action = "store_true", help = "Create a pretty-printed output JSON file.")
			parser.add_argument("outfile", nargs='?', help = "Output JSON file")
		multicommand.register("bp2json", "Convert a blueprint to JSON", genparser, action = ActionBlueprintToJSON)
