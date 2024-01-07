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
import collections
import enum
import json
import math
import os

from BaseAction import BaseAction
from dspbp.Blueprint import Blueprint
from dspbp.Enums import DysonSphereItem as dsi, Recipe
from dspbp.Utils import maybeDysonSphereItem, maybeRecipe
from dspbp.Recipes import ItemProduction, RECIPE_MAP, Machine
from dspbp.Assess import Assessment
import dspbp.Recipes as Recipes

REPRESENTATION_MAP = {
	# Tech levels
	0 : '0',
	1 : 'I',
	2 : 'II',
	3 : 'III',
	4 : 'IV',
	5: 'V',
	6: 'VI',
	7: 'VII',
	# Proliferator
	dsi.ProliferatorMkI : '+1',
	dsi.ProliferatorMkII : '+2',
	dsi.ProliferatorMkIII : '+3',
}

ADVANCED_RECIPE_MAP = {
	Recipe.CasimirCrystalAdvanced : dsi.OpticalGratingCrystal,
	Recipe.GrapheneAdvanced : dsi.FireIce,
	Recipe.CarbonNanotubeAdvanced : dsi.SpiniformStalagmiteCrystal,
	Recipe.DiamondAdvanced: dsi.KimberliteOre,
	Recipe.CrystalSiliconAdvanced: dsi.FractalSilicon,
	Recipe.PhotonCombinerAdvanced : dsi.OpticalGratingCrystal,
	Recipe.ParticleContainerAdvanced: dsi.UnipolarMagnet,
}

ICON_LAYOUT_MAP = {
	10: 1,
	20: 2, # Two, side-by-side
	21: 2, # Lower right corner
	22: 2, # Upper right corner
	23: 2, # Upper left corner
	32: 3, # Big middle, upper left, lower right
}

class ActionAnnotate(BaseAction):
	def run(self):
		for filename, bp in self.blueprints(self._args.inputs):
			assessment = Assessment(bp)

			tech_level = max(Machine.registry[item_id].tech_level if item_id in Machine.registry else 0 for item_id in assessment.building_counter)

			additional_imports = []
			for import_ in assessment.imports:
				if import_ not in assessment.inputs:
					additional_imports.append(import_)

			additional_exports = []
			for export_ in assessment.exports:
				if export_ not in assessment.outputs:
					additional_exports.append(export_)

			if self._args.verbose:
				print(f'Blueprint source: {filename}')
				print(f'Unique building types: {len(assessment.building_counter)}, unique recipies: {len(assessment.recipe_counter)}')
				print(f'Tech level: {tech_level}')
				print(f'Area: {assessment.size_assessment} | {assessment.size_assessment.height_scale} | { assessment.size_assessment.sector_widths }')

				print('Machine recap:')
				for ((item_type_id, recipe_id), amount) in assessment.building_recipe_counter.most_common():
					recipe = None if recipe_id == 0 else (maybeRecipe(recipe_id) or f'[{recipe_id} (recipe)]')
					item_type = maybeDysonSphereItem(item_type_id) or f'[{building.data.item_id}]'
					print("%5d  %25s %20s (%s)" % (amount, item_type.name, getattr(recipe, 'name', recipe), recipe))

				if additional_imports:
					print(f'Additional imports: {', '.join(import_.name for import_ in additional_imports)}')
				if additional_exports:
					print(f'Additional exports: {', '.join(export_.name for export_ in additional_exports)}')

			primary_output_id = assessment.primary_output_id
			if self._args.verbose:
				print(f'Primary output: { primary_output_id.name if isinstance(primary_output_id, enum.IntEnum) else (primary_output_id or None) } @ {round(assessment.primary_output_amount,1)}/sec')

			# Folder name is once of:
			# - Science/Science - Type
			# - Intermediate Products
			# - Smelters
			# - (anything else?)
			# - Original location
			folder = os.path.dirname(filename)
			blueprint_root, sep, _ = folder.partition('Blueprint')
			blueprint_root = blueprint_root + sep
			if primary_output_id in [
				dsi.ElectromagneticMatrix, dsi.EnergyMatrix, dsi.StructureMatrix, dsi.InformationMatrix, dsi.GravityMatrix,
				dsi.UniverseMatrix]:
				folder = os.path.join(blueprint_root,'Science', f'Science - {primary_output_id.name}')
			elif primary_output_id in [
				dsi.StoneBrick, dsi.Glass, dsi.IronIngot, dsi.Magnet, dsi.CopperIngot, dsi.TitaniumIngot,
				dsi.TitaniumAlloy, dsi.CrystalSilicon, dsi.HighPuritySilicon, dsi.EnergeticGraphite, dsi.Diamond,
				]:
				folder = os.path.join(blueprint_root,'Smelters')
			else:
				folder = os.path.join(blueprint_root,'Intermediate Products')
			if self._args.verbose:
				print(f'Folder: {folder}')

			# Filename is: [PrimaryOutput] [Scale][Width][Proliferation]-[TechLevel]-[RecipeCount][AdvancedRecipies] [Quantity]
			# where
			#   - one `i` is used for each advanced recipe used
			#   - '+1', '+2', or '+3' is used if proliferation is used
			#   - Tech level is 1 to 7 in Roman numerals
			#   - Scale is P (planetary), A, B, or C depending on where the blueprint fits
			#   - Width is the number of sectors wide the blueprint is
			#
			# The overall goal is to make it easy to have unique blueprint names that can be leveled up/down
			# Short description matches filename

			advanced_recipe_items = [item for recipe, item in ADVANCED_RECIPE_MAP.items() if recipe in assessment.recipe_counter]
			advanced_recipe_count = sum(1 if item else 0 for item in advanced_recipe_items)
			advanced_recipe_icon = advanced_recipe_items[0] if advanced_recipe_items else None

			primary_production_building = [Recipes.Machine.registry.get(building, None) for building in assessment.building_counter]
			if not primary_production_building:
				primary_production_building = None
			else:
				primary_production_building = [building.machine_id for building in primary_production_building if building][0]

			short_description = f'{primary_output_id.name if hasattr(primary_output_id, 'name') else primary_output_id} {round(assessment.primary_output_amount,1):5}ips ({assessment.size_assessment.height_scale}{ assessment.size_assessment.sector_widths }{REPRESENTATION_MAP.get(assessment.proliferate, '')}-{REPRESENTATION_MAP.get(tech_level, '')}-{len(assessment.recipe_counter)}{'i' * advanced_recipe_count})'
			if self._args.verbose:
				print(short_description)

			# Icons
			if self._args.verbose:
				print(f'Icon layout: {bp._layout} ({ICON_LAYOUT_MAP.get(bp._layout,'?')}) -- {', '.join(str(icon) for icon in [bp._icon0, bp._icon1, bp._icon2, bp._icon3, bp._icon4])}')

			icons = [advanced_recipe_icon, primary_production_building, assessment.proliferate]
			icon_count = len([icon for icon in icons if icon])

			bp._icon0 = primary_output_id
			if icon_count == 0:
				bp._layout = 10
			elif icon_count == 1 and assessment.proliferate:
				bp._layout = 22
				bp._icon1 = assessment.proliferate
			elif icon_count == 1:
				bp._layout = 23
				bp._icon1 = advanced_recipe_icon or primary_production_building
			else:
				bp._layout = 32
				bp._icon1 = advanced_recipe_icon or primary_production_building
				bp._icon2 = proliferate or primary_production_building

			if self._args.verbose:
				print(f'Updated Icon layout: {bp._layout} ({ICON_LAYOUT_MAP.get(bp._layout,'?')}) -- {', '.join(str(icon) for icon in [bp._icon0, bp._icon1, bp._icon2, bp._icon3, bp._icon4])}')

			# Long description
			pieces = []
			pieces += [f'{output.name}: {round(amount, 1)}/sec' for output, amount in assessment.outputs.items()]
			pieces += ['', 'Inputs:']
			pieces += [f'    {input.name:20}: {round(amount, 1):6}/sec' for input, amount in assessment.inputs.items()]
			pieces += ['']
			if additional_imports:
				pieces.append(f'Additional imports: {', '.join(import_.name for import_ in additional_imports)}')
			if additional_exports:
				pieces.append(f'Additional exports: {', '.join(export_.name for export_ in additional_exports)}')

			long_description = '\n'.join(pieces)
			if self._args.verbose:
				print(f'Long description:\n{long_description}\n---')
				print()

			if ' of ' in filename:
				print(f'Skipping annotation of {filename} as part of set')
				continue

			if short_description == bp.short_desc:
				pass
			elif self._args.override_text or not bp.short_desc:
				bp.short_desc = short_description
			else:
				print('Skipping short description rewrite')

			if long_description == bp.long_desc:
				pass
			elif self._args.override_text or not bp.long_desc:
				if self._args.verbose:
					print('Overwriting long description...')
				bp.long_desc = long_description
			else:
				print('Skipping long description rewrite')

			head, tail = os.path.split(filename)
			final_name = f'{os.path.join(
				folder if self._args.move else head,
				short_description if self._args.rename else tail
			)}.txt'
			should_rename = not os.path.exists(final_name) or not os.path.samefile(final_name, filename)

			if self._args.verbose:
				print(f'Final filename: {final_name} ({'will rename' if should_rename else 'no rename'})')
			if self._args.dry_run:
				continue

			bp.write_to_file(final_name)

			if should_rename:
				if self._args.verbose:
					print(f'Removing {filename}...')
				os.remove(filename)

	@classmethod
	def register(cls, multicommand):
		def genparser(parser):
			cls._genparser(parser, is_folder_search=True)
			parser.add_argument("-r", '--rename', action='store_true', help='Also rename blueprints')
			parser.add_argument("-m", '--move', action='store_true', help='Also move blueprints')
			parser.add_argument("-b", '--override-text', action='store_true', help='Override non-blank descriptions and icons')
		multicommand.register("annotate", "Annotate blueprint descriptions and icons", genparser, action = cls)
