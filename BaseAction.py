#	dspbptk - Dyson Sphere Program Blueprint Toolkit
#	Copyright (C) 2021-2021 Johannes Bauer
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

from dspbp.Blueprint import Blueprint
import envshim


def _is_blueprint(input):
	return input.startswith('BLUEPRINT:')

def _input_to_path(input):
	if os.path.exists(input):
		return input
	alternate_input = os.path.join(envshim.ENV['root'], input)
	if os.path.exists(alternate_input):
		return alternate_input
	print(f'Unable to locate `{input}`')
	return input  # Should this error?

class BaseAction():
	def __init__(self, cmdname, args):
		self._cmd = cmdname
		self._args = args
		envshim.load_env()
		self.run()

	def run(self):
		raise NotImplementedError()

	@classmethod
	def register(cls, _):
		raise NotImplementedError()

	def find_blueprints(self, inputs):
		"""
		Find all blueprint files given a list of files and/or directories

		Typical usage:
			blueprint_files = self.find_blueprints(self._args.inputs)
		"""
		input_files = []
		for input in inputs:
			if os.path.isfile(input):
				input_files.append(input)
			elif os.path.isdir(input):
				for root, _, files in os.walk(input):
					if self._args.verbose > 0:
						print(f'Searching {root}...')

					for blueprint_file in files:
						if blueprint_file == '_intro_' or not blueprint_file.endswith('.txt'):
							continue
						input_files.append(os.path.join(root, blueprint_file))
					if not self._args.should_recurse:
						break
			else:
				raise ValueError(f'Unknown input {input}')
		return input_files

	def blueprints(self, inputs):
		# Capture all files so we don't grab more files as we rename them
		blueprint_files = [filename for filename in self.find_blueprints(_input_to_path(input) for input in inputs if input and not _is_blueprint(input))]
		for filename in blueprint_files:
			yield filename, Blueprint.read_from_file(filename, validate_hash = not self._args.ignore_corrupt)
		for input in inputs:
			if not input or not input.startswith('BLUEPRINT:'):
				continue
			yield None, Blueprint.from_blueprint_string(input, validate_hash = not self._args.ignore_corrupt)
		try:
			import pyperclip
			maybe_blueprint = pyperclip.paste()
			if _is_blueprint(maybe_blueprint):
				yield None, Blueprint.from_blueprint_string(maybe_blueprint, validate_hash = not self._args.ignore_corrupt)
		except ImportError:
			pass


	@classmethod
	def _genparser(cls, parser, is_single_file=False, is_folder_search=False):
		if is_single_file and is_folder_search:
			raise ValueError('Cannot use single file mode and folder search mode together.')
		if is_single_file or is_folder_search:
			parser.add_argument("--ignore-corrupt", action = "store_true", help = "Do not validate the checksum when reading the blueprint file.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity.")
		parser.add_argument("-n", "--dry-run", action="store_true", help="Only show what would be changed")
		if is_folder_search:
			parser.add_argument("--no-recurse", dest='should_recurse', action="store_false", help='Do not recurse ')
			parser.add_argument("inputs", nargs = "*", help = "Input blueprint file(s) and/or directory(s)")
		if is_single_file:
			parser.add_argument("infile", nargs = '?', help = "Input blueprint text file (buildings will be replaced)")
