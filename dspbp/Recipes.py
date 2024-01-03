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

from .Enums import Recipe, DysonSphereItem as dsi


class Machine:
    registry = {}
    def __init__(self, machine_id, downgrade_machine_id=None, production_multiplier=1, tech_level=1):
        self.machine_id = machine_id
        self.tech_level = tech_level
        self.downgrade_machine = self.registry[downgrade_machine_id] if downgrade_machine_id else None
        self.production_multiplier = production_multiplier
        self.upgrade_machine = None
        self.registry[machine_id] = self
        if self.downgrade_machine:
            self.downgrade_machine.set_upgrade(self)

    def set_upgrade(self, machine):
        self.upgrade_machine = machine

    def find_tech_level_equivalent_machine(self, tech_level=0):
        """Find the right machine for the corresponding tech level"""
        if self.tech_level > tech_level and self.downgrade_machine:
            return self.downgrade_machine.find_tech_level_equivalent_machine(tech_level)
        if self.upgrade_machine and self.upgrade_machine.tech_level <= tech_level:
            return self.upgrade_machine.find_tech_level_equivalent_machine(tech_level)
        return self.machine_id

Machine(dsi.AssemblingMachineMkI, None, 0.75)
Machine(dsi.AssemblingMachineMkII, dsi.AssemblingMachineMkI, tech_level=3)
Machine(dsi.AssemblingMachineMkIII, dsi.AssemblingMachineMkII, 1.5, tech_level=5)
Machine(dsi.MatrixLab)
Machine(dsi.ArcSmelter)
Machine(dsi.PlaneSmelter, dsi.ArcSmelter, 2, tech_level=6)
Machine(dsi.MiniatureParticleCollider, tech_level=4)
Machine(dsi.ChemicalPlant)
Machine(dsi.QuantumChemicalPlant, dsi.ChemicalPlant, 2, tech_level=6)
Machine(dsi.OilRefinery)

# For now, no speedup mode
PROLIFERATION_PRODUCT_MULTIPLIERS = {
    dsi.ProliferatorMkIII : 1.25,
    dsi.ProliferatorMkII : 1.2,
    dsi.ProliferatorMkI : 1.125,
}

def get_production_multiple(machine):
    try:
        return Machine.registry[machine].production_multiplier
    except KeyError:
        if isinstance(machine, enum.IntEnum):
            raise KeyError(f'Unknown production multiple {machine.name}')
        else:
            raise KeyError(f'Unknown production multiple {machine}')

class RecipeDetails:
    def __init__(self, inputs, outputs, period):
        """
            inputs: itemId ==> amount
            outputs: itemId ==> amount
            period: Length of time (seconds)
        """
        self.inputs = inputs
        self.outputs = outputs
        self.period = period

    def calculate_outputs(self, machines, proliferate=None):
        """
        Takes in integer or map of machines to machine count
        """
        production_multiple = machines
        if not isinstance(machines, int):
            production_multiple = sum(
                get_production_multiple(machine) * machine_count for machine, machine_count in machines.items()
                )
        production_multiple /= self.period
        try:
            production_multiple *= PROLIFERATION_PRODUCT_MULTIPLIERS[proliferate] if isinstance(proliferate, enum.IntEnum) \
                else proliferate if isinstance(proliferate, int) \
                else 1
        except KeyError:
            print(f'Unknown proliferation item {proliferate.name}')
        return {
            product : items * production_multiple for product, items in self.outputs.items()
        }
    def calculate_inputs(self, machines):
        production_multiple = machines
        if not isinstance(machines, int):
            production_multiple = sum(get_production_multiple(machine) * machine_count for machine, machine_count in machines.items())
        production_multiple /= self.period
        return {
            product : items * production_multiple for product, items in self.inputs.items()
        }


class ItemProduction:
    """
    Represents a collection
    """
    def __init__(self, collection=None):
        self._items = collection or {}

    def items(self):
        return self._items.items()

    def __add__(self, a):
        b = collections.defaultdict(int)
        for item, amount in self.items():
            b[item] = amount
        for item, amount in a.items():
            b[item] += amount
        return ItemProduction(b)

    def __sub__(self, a):
        b = collections.defaultdict(int)
        for item, amount in self.items():
            b[item] = amount
        for item, amount in a.items():
            b[item] -= amount
        return ItemProduction(b)

    def __str__(self):
        entries = [[amount, item] for item, amount in self.items()]
        entries.sort()
        lines = []
        previous_type = None
        for amount, item in entries:
            type_ = 'Output'
            if amount < 0:
                type_ = 'Input'
                amount = -amount
            elif amount == 0:
                continue
            if previous_type != type_:
                lines.append(f'{type_}:')
                previous_type = type_
            lines.append(f'    {item.name:25} {round(amount,2):5}/s | {round(amount*60,1):5}/min ')
        return '\n'.join(lines)

    @property
    def primary_output(self):
        prior_item = None
        prior_amount = 0
        for item, amount in self.items():
            if amount <= 0:  # Ignore inputs
                continue
            # Hydrogen is a byproduct and almost never the intended output
            if not prior_item or prior_amount < amount or prior_item == dsi.Hydrogen:
                prior_item = item
                prior_amount = amount
        return prior_item, prior_amount

RECIPE_MAP = {
    Recipe.Foundation: RecipeDetails({ dsi.Steel : 1, dsi.StoneBrick: 3 }, { dsi.Foundation: 1 }, 3),
    Recipe.Gear: RecipeDetails({ dsi.IronIngot : 1 }, { dsi.Gear: 1 }, 1),

    Recipe.MagneticCoil: RecipeDetails({ dsi.CopperIngot : 1, dsi.Magnet : 2}, { dsi.MagneticCoil: 2,}, 1),
    Recipe.ElectricMotor: RecipeDetails({ dsi.MagneticCoil : 1, dsi.IronIngot : 2, dsi.Gear : 1}, { dsi.ElectricMotor: 1,}, 2),
    Recipe.ElectromagneticTurbine: RecipeDetails({ dsi.ElectricMotor : 2, dsi.MagneticCoil : 2 }, { dsi.ElectromagneticTurbine: 1,}, 2),
    Recipe.SuperMagneticRing: RecipeDetails({ dsi.ElectromagneticTurbine : 2, dsi.EnergeticGraphite : 3, dsi.Magnet : 1}, { dsi.SuperMagneticRing: 1,}, 3),
    Recipe.ParticleContainer: RecipeDetails({ dsi.ElectromagneticTurbine : 2, dsi.CopperIngot : 2}, { dsi.ParticleContainer: 1 }, 4),

    Recipe.CircuitBoard: RecipeDetails({ dsi.CopperIngot : 1, dsi.IronIngot : 2}, { dsi.CircuitBoard: 2}, 1),
    Recipe.MicrocrystallineComponent: RecipeDetails({ dsi.HighPuritySilicon : 2, dsi.CopperIngot : 1}, { dsi.MicrocrystallineComponent: 1 }, 3),
    Recipe.Processor: RecipeDetails({ dsi.CircuitBoard : 2, dsi.MicrocrystallineComponent : 2}, { dsi.Processor: 1 }, 3),

    Recipe.Prism: RecipeDetails({ dsi.Glass : 3 }, { dsi.Prism: 2}, 2),
    Recipe.PlasmaExciter: RecipeDetails({ dsi.Prism : 2, dsi.MagneticCoil: 4 }, { dsi.PlasmaExciter: 1}, 2),
    Recipe.PhotonCombiner: RecipeDetails({ dsi.Prism : 2, dsi.CircuitBoard: 1 }, { dsi.PhotonCombiner: 1}, 3),
    Recipe.PhotonCombinerAdvanced: RecipeDetails({ dsi.OpticalGratingCrystal : 1, dsi.CircuitBoard: 1 }, { dsi.PhotonCombiner: 1}, 3),

    Recipe.FrameMaterial: RecipeDetails({ dsi.CarbonNanotube : 4, dsi.TitaniumAlloy : 1, dsi.HighPuritySilicon: 1}, { dsi.FrameMaterial: 1 }, 6),
    Recipe.DysonSphereComponent: RecipeDetails({ dsi.FrameMaterial : 3, dsi.SolarSail : 3, dsi.Processor: 3},{ dsi.DysonSphereComponent: 1 }, 8),
    Recipe.SmallCarrierRocket: RecipeDetails({ dsi.DysonSphereComponent : 2, dsi.QuantumChip : 2, dsi.DeuteronFuelRod: 4},{ dsi.SmallCarrierRocket: 1 }, 6),

    Recipe.QuantumChip: RecipeDetails({ dsi.Processor:2, dsi.PlaneFilter: 2}, { dsi.QuantumChip : 1}, 6),

    Recipe.GravitonLens : RecipeDetails({ dsi.Diamond : 4, dsi.StrangeMatter : 1},{ dsi.GravitonLens: 1 }, 6),
    Recipe.ParticleBroadband : RecipeDetails({ dsi.CarbonNanotube : 2, dsi.CrystalSilicon : 2, dsi.Plastic: 1},{ dsi.ParticleBroadband: 1 }, 8),
    Recipe.SpaceWarperAdvanced : RecipeDetails({ dsi.GravityMatrix : 1}, { dsi.SpaceWarper : 8}, 10),

    Recipe.TitaniumGlass: RecipeDetails({ dsi.Glass: 2, dsi.TitaniumIngot: 2, dsi.Water: 2}, { dsi.TitaniumGlass : 2}, 5),
    Recipe.TitaniumCrystal: RecipeDetails({ dsi.OrganicCrystal : 1, dsi.TitaniumIngot : 3}, { dsi.TitaniumCrystal: 1 }, 4),
    Recipe.CasimirCrystal: RecipeDetails({ dsi.TitaniumCrystal: 1, dsi.Graphene: 2, dsi.Hydrogen: 12}, { dsi.CasimirCrystal : 1}, 4),
    Recipe.CasimirCrystalAdvanced: RecipeDetails({ dsi.OpticalGratingCrystal: 8, dsi.Graphene: 2, dsi.Hydrogen: 12}, { dsi.CasimirCrystal : 1}, 4),
    Recipe.PlaneFilter: RecipeDetails({ dsi.TitaniumGlass: 2, dsi.CasimirCrystal: 1}, { dsi.PlaneFilter : 1}, 12),

    Recipe.HydrogenFuelRod: RecipeDetails({ dsi.TitaniumIngot : 1, dsi.Hydrogen : 10}, { dsi.HydrogenFuelRod: 2 }, 6),
    Recipe.DeuteronFuelRod: RecipeDetails({ dsi.TitaniumAlloy : 1, dsi.SuperMagneticRing: 1, dsi.Deuterium : 20}, { dsi.DeuteronFuelRod: 2 }, 12),
    Recipe.AntimatterFuelRod: RecipeDetails({ dsi.TitaniumAlloy : 1, dsi.AnnihilationConstraintSphere: 1, dsi.Hydrogen : 12, dsi.Antimatter: 12}, { dsi.AntimatterFuelRod: 2 }, 24),

    # Ammo
    Recipe.MagnumAmmoBox: RecipeDetails({ dsi.CopperIngot : 4}, { dsi.MagnumAmmoBox: 1 }, 1),
    Recipe.TitaniumAmmoBox: RecipeDetails({ dsi.TitaniumIngot : 2, dsi.MagnumAmmoBox: 1}, { dsi.TitaniumAmmoBox: 1 }, 2),
    Recipe.TitaniumAlloyAmmoBox: RecipeDetails({ dsi.TitaniumAlloy : 2, dsi.TitaniumAmmoBox: 1}, { dsi.TitaniumAlloyAmmoBox: 1 }, 3),

    # Science
    Recipe.ElectromagneticMatrix: RecipeDetails({ dsi.CircuitBoard: 1, dsi.MagneticCoil : 1}, {dsi.ElectromagneticMatrix: 1}, 3),
    Recipe.EnergyMatrix: RecipeDetails({ dsi.EnergeticGraphite: 2, dsi.Hydrogen : 2}, {dsi.EnergyMatrix: 1}, 6),
    Recipe.StructureMatrix : RecipeDetails({ dsi.TitaniumCrystal: 1, dsi.Diamond : 1}, {dsi.StructureMatrix: 1}, 8),
    Recipe.InformationMatricx : RecipeDetails({ dsi.Processor: 2, dsi.ParticleBroadband : 1}, {dsi.InformationMatrix: 1}, 10),
    Recipe.GravityMatrix : RecipeDetails({ dsi.GravitonLens: 1, dsi.QuantumChip : 2}, {dsi.GravityMatrix: 2}, 24),
    Recipe.UniverseMatrix: RecipeDetails({ dsi.ElectromagneticMatrix: 1, dsi.EnergyMatrix : 1, dsi.StructureMatrix : 1, dsi.InformationMatrix: 1, dsi.GravityMatrix: 1, dsi.Antimatter: 1}, {dsi.UniverseMatrix: 1}, 15),

    # Smelting
    Recipe.IronIngot: RecipeDetails({ dsi.IronOre : 1}, { dsi.IronIngot: 1,}, 1),
    Recipe.Magnet: RecipeDetails({ dsi.IronOre : 1}, { dsi.Magnet: 1,}, 1.5),
    Recipe.Steel: RecipeDetails({ dsi.IronIngot : 3}, { dsi.Steel: 1,}, 3),
    Recipe.CopperIngot: RecipeDetails({ dsi.CopperOre : 1}, { dsi.CopperIngot: 1,}, 1),
    Recipe.HighPuritySilicon: RecipeDetails({ dsi.SiliconOre : 1}, { dsi.HighPuritySilicon: 1,}, 2),
    Recipe.TitaniumIngot: RecipeDetails({ dsi.TitaniumOre : 1}, { dsi.TitaniumIngot: 1,}, 2),
    Recipe.EnergeticGraphite: RecipeDetails({ dsi.Coal : 1}, { dsi.EnergeticGraphite: 1,}, 2),
    Recipe.StoneBrick: RecipeDetails({ dsi.Stone : 1}, { dsi.StoneBrick: 1,}, 1),
    Recipe.Glass: RecipeDetails({ dsi.Stone : 2}, { dsi.Glass: 1,}, 2),
    Recipe.Diamond : RecipeDetails({ dsi.EnergeticGraphite : 1}, { dsi.Diamond: 1,}, 2),
    Recipe.DiamondAdvanced : RecipeDetails({ dsi.KimberliteOre : 1}, { dsi.Diamond: 2,}, 1.5),
    Recipe.TitaniumAlloy: RecipeDetails({ dsi.TitaniumIngot : 4, dsi.Steel : 4, dsi.SulfuricAcid : 4}, { dsi.TitaniumAlloy: 4,}, 12),
    Recipe.CrystalSilicon: RecipeDetails({ dsi.HighPuritySilicon : 1}, { dsi.CrystalSilicon: 1,}, 2),

    # Particle collider
    Recipe.Deuterium: RecipeDetails({ dsi.Hydrogen : 24}, { dsi.Deuterium: 12}, 6),
    Recipe.StrangeMatter : RecipeDetails({ dsi.IronIngot : 2, dsi.ParticleContainer : 2, dsi.Deuterium : 10}, { dsi.StrangeMatter: 1,}, 8),

    # Refinery
    Recipe.PlasmaRefining: RecipeDetails({ dsi.CrudeOil : 2}, { dsi.RefinedOil: 2, dsi.Hydrogen: 1 }, 4),
    Recipe.XRayCracking: RecipeDetails({ dsi.RefinedOil: 1, dsi.Hydrogen: 2}, { dsi.EnergeticGraphite: 1, dsi.Hydrogen: 3 }, 4),

    # Chemistry
    Recipe.SulfuricAcid: RecipeDetails({ dsi.Stone : 4, dsi.RefinedOil : 3, dsi.Water: 2}, { dsi.SulfuricAcid: 2 }, 3),
    Recipe.Plastic: RecipeDetails({ dsi.RefinedOil : 2, dsi.EnergeticGraphite : 1}, { dsi.Plastic: 1 }, 3),
    Recipe.Graphene: RecipeDetails({ dsi.EnergeticGraphite : 3, dsi.SulfuricAcid: 1 }, { dsi.Graphene: 2 }, 3),
    Recipe.GrapheneAdvanced: RecipeDetails({ dsi.FireIce : 2 }, { dsi.Graphene: 2, dsi.Hydrogen: 1 }, 2),
    Recipe.CarbonNanotube: RecipeDetails({ dsi.Graphene : 3, dsi.TitaniumIngot: 1 }, { dsi.CarbonNanotube: 2 }, 4),
    Recipe.OrganicCrystal : RecipeDetails({ dsi.Plastic : 2, dsi.RefinedOil: 1, dsi.Water: 1}, { dsi.OrganicCrystal : 8}, 6),
}