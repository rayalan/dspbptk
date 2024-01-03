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

class BaseAction():
	def __init__(self, cmdname, args):
		self._cmd = cmdname
		self._args = args
		self.run()

	def run(self):
		raise NotImplementedError()

	@classmethod
	def register(cls, _):
		raise NotImplementedError()

	@staticmethod
	def find_blueprints(inputs, verbosity=0):
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
					if verbosity > 0:
						print(f'Searching {root}...')

					for blueprint_file in files:
						if blueprint_file == '_intro_' or not blueprint_file.endswith('.txt'):
							continue
						input_files.append(os.path.join(root, blueprint_file))
			else:
				raise ValueError(f'Unknown input {input}')
		return input_files

	@staticmethod
	def blueprints(inputs, verbosity=0, should_ignore_corruption=False):
		for filename in BaseAction.find_blueprints(input for input in inputs if not input.startswith('BLUEPRINT:')):
			yield filename, Blueprint.read_from_file(filename, validate_hash = not should_ignore_corruption)
		for input in inputs:
			print(input)
			if not input.startswith('BLUEPRINT:'):
				continue
			yield None, Blueprint.from_blueprint_string(input, validate_hash = not should_ignore_corruption)
