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

from BaseAction import BaseAction
from dspbp.Assess import Assessment

def read_clipboard_blueprint():
	try:
		import pyperclip
		return pyperclip.paste()
	except ImportError:
		raise SystemExit('Unable to read clipboard (pyperclip not installed). Run `pip3 install pyperclip`.')


class ActionReplace(BaseAction):
	def run(self):
		best_blueprint = None
		target_filename = None

		match_score = -1
		replacement_source = self._args.replacement	if self._args.replacement else read_clipboard_blueprint()
		_, replacement_blueprint = next(self.blueprints([replacement_source]))
		replacement_assessment = Assessment(replacement_blueprint)
		for filename, original_blueprint in self.blueprints([self._args.infile]):
			if not filename:
				print('Skipping non-filename blueprint as possible blueprint to replace')
				continue
			print(f'Assessing `{filename}` for a match...')
			original_assessment = Assessment(original_blueprint)

			# How do we tell if a blueprint should be considered a likely replacement candidate?
			# - Inputs and output types
			# - Number and type of production buildings
			# - Number of type of recipes
			# - Total number of belts (lesser factor)
			# - Different sized area
			#
			# We don't care about
			# - Number of sorters (largely determined by buildings + recipes)
			# - Number of traffic monitors or proliferation
			#
			# All difference factors are experimental for now.
			difference_score = 1

			for import_ in original_assessment.imports:
				if import_ not in replacement_assessment.imports:
					difference_score += 1
			for import_ in replacement_assessment.imports:
				if import_ not in original_assessment.imports:
					difference_score += 1
			for export_ in original_assessment.exports:
				if export_ not in replacement_assessment.exports:
					difference_score += 1
			for export_ in replacement_assessment.exports:
				if export_ not in original_assessment.exports:
					difference_score += 1

			if difference_score > 0 and (difference_score < match_score or match_score < 0) :
				best_blueprint = original_blueprint
				target_filename = filename
				match_score = difference_score

		if not target_filename or not best_blueprint:
			raise ValueError('No blueprint to replace identified.')

		if not self._args.force:
			prompt = input(f'Confirm replacement of blueprint in `{target_filename}` [y/N]: ')
			if prompt.lower() not in ['y', 'yes']:
			     raise KeyboardInterrupt('Replacement not confirmed.')

		best_blueprint._data = replacement_blueprint._data
		if  self._args.dry_run:
			print('Skipping write due to dry run')
		else:
			best_blueprint.write_to_file(target_filename)

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			cls._genparser(parser, is_single_file=True)
			parser.add_argument("replacement", nargs='?', help = "The file or blueprint string to use as the replacement. Uses clipboard by default")
			parser.add_argument('-f', '--force', action='store_true', help = "Force replacement without confirmation")

		multicommand.register("replace", "Replace the buildings (but not the files, descriptions, or icons) of one blueprint with another", genparser, action = cls)

