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
import os

from BaseAction import BaseAction
from dspbp.Blueprint import Blueprint


class ActionValidateSerialize(BaseAction):
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

		validated_count = 0

		for input_file in input_files:
			bp = Blueprint.read_from_file(input_file, validate_hash = not self._args.ignore_corrupt)
			bpd = bp.decoded_data
			serialized_data = bpd.serialize()

			if bp._data == serialized_data:
				validated_count += 1
			else:
				print(f'Blueprint did not serialize as expected: {input}')

		print(f'Validated {validated_count} of {len(input_files)} blueprints.')
		if validated_count != len(input_files):
			print('Please submit a bug report for blueprints that did not serialize.')

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			parser.add_argument("--ignore-corrupt", action = "store_true", help = "Do not validate the checksum when reading the blueprint file.")
			parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity.")
			parser.add_argument("inputs", nargs = "+", help = "Validation blueprint file(s) and/or directory(s)")
		multicommand.register("validate-serialize", "Validate blueprints can be reserialized", genparser, action = cls)
