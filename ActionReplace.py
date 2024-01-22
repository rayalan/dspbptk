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

def read_clipboard_blueprint():
	try:
		import pyperclip
		return pyperclip.paste()
	except ImportError:
		raise SystemExit('Unable to read clipboard (pyperclip not installed). Run `pip3 install pyperclip`.')


class ActionReplace(BaseAction):
	def run(self):
		filename, original_blueprint = next(self.blueprints([self._args.infile]))

		replacement_source = self._args.replacement	if self._args.replacement else read_clipboard_blueprint()
		_, replacement_blueprint = next(self.blueprints([replacement_source]))
		original_blueprint._data = replacement_blueprint._data
		if not filename:
			raise ValueError('Original blueprint must have name in order to replace it')
		original_blueprint.write_to_file(self._args.infile)

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			cls._genparser(parser, is_single_file=True)
			parser.add_argument("replacement", nargs='?', help = "The file or blueprint string to use as the replacement. Uses clipboard by default")

		multicommand.register("replace", "Replace the buildings (but not the files, descriptions, or icons) of one blueprint with another", genparser, action = cls)

