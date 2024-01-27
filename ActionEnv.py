import os
import json

from BaseAction import BaseAction
import envshim

class ActionEnv(BaseAction):
	def run(self):
		if self._args.clear:
			self.delete_env()
		elif self._args.key_value_pairs:
			self.set_env()
		else:
			self.print_env()

	def delete_env(self):
		pass

	def print_env(self):
		print(f'Environment location: {envshim.ENV_PATH}')
		if os.path.isfile(envshim.ENV_PATH):
			# envshim.load_env()
			pass
		else:
			print('No environment variables defined.')
		for key, (help_text, default_value) in envshim.ENV_VAR_DEFINITIONS.items():
			print(f'{key:20} {envshim.ENV.get(key, 'n/a'):20}\n\tdefault: {default_value:20}\n\t{help_text}')

		if 'root' in envshim.ENV:
			print(f'Blueprint path: {'valid' if os.path.isdir(envshim.ENV['root']) else 'invalid'}')
		try:
			import pyperclip
			print('Read from clipboard: valid')
		except ImportError:
			print('Read from clipboard: failed (try `pip3 install pyperclip`)')


	def set_env(self):
		# load_env()
		for input in self._args.key_value_pairs:
			key, value = input.split(':')
			if value:
				envshim.ENV[key] = value
			else:
				del envshim.ENV[key]
		json.dump(envshim.ENV, open(envshim.ENV_PATH, 'w'))

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			cls._genparser(parser, is_folder_search=False, is_single_file=False)
			parser.add_argument('--clear', action='store_true', help='Delete environment definitions')
			parser.add_argument('key_value_pairs', nargs='*', help='Set environment `key:value` for future commands; use `key:` to clear.')
		multicommand.register("env", "Manipulate environment variables", genparser, action = cls)
