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

import enum

class Recipe(enum.IntEnum):
	IronIngot = 1
	Magnet = 2
	CopperIngot = 3
	StoneBrick = 4
	Gear = 5
	MagneticCoil = 6
	Prism = 11
	PlasmaExciter = 12
	PlasmaRefining = 16
	EnergeticGraphite = 17
	HydrogenFuelRod = 19
	Thruster = 20
	ReinforcedThruster = 21
	Plastic = 23
	SulfuricAcid = 24
	OrganicCrystal=25
	TitaniumCrystal = 26
	CasimirCrystal = 28
	CasimirCrystalAdvanced = 29
	TitaniumGlass = 30
	Graphene = 31
	GrapheneAdvanced = 32
	CarbonNanotube = 33
	Silicon = 34 # From stone
	CarbonNanotubeAdvanced = 35
	ParticleBroadband = 36
	CrystalSilicon = 37
	PlaneFilter = 38
	Deuterium = 40
	DeuteronFuelRod = 41
	AnnihilationConstraintSphere = 42
	AntimatterFuelRod = 44
	CircuitBoard = 50
	Processor = 51
	QuantumChip = 52
	MicrocrystallineComponent = 53
	OrganicCrystalOriginal = 54
	Glass = 57
	XRayCracking = 58
	HighPuritySilicon = 59
	Diamond = 60
	DiamondAdvanced = 61
	CrystalSiliconAdvanced = 62
	Steel = 63
	TitaniumIngot = 65
	TitaniumAlloy = 66
	PhotonCombiner = 68
	PhotonCombinerAdvanced = 69
	SolarSail = 70
	SpaceWarper = 78
	SpaceWarperAdvanced = 79
	FrameMaterial = 80
	DysonSphereComponent = 81
	SmallCarrierRocket = 83
	LogisticsDrone = 94
	LogisticsVessel = 96
	ElectricMotor = 97
	ElectromagneticTurbine = 98
	ParticleContainer = 99
	ParticleContainerAdvanced = 100
	GravitonLens = 101
	SuperMagneticRing = 103
	StrangeMatter = 104
	Engine = 105
	ProliferatorI = 106
	ProliferatorII = 107
	ProliferatorIII = 108
	Foundation = 112
	DeuteriumFractionation = 115
	ReformingRefine = 121
	LogisticsBot = 123
	CombustibleUnit = 133
	ExplosiveUnit = 134
	CrystalExplosiveUnit = 135
	MagnumAmmoBox = 136
	TitaniumAmmoBox = 137
	TitaniumAlloyAmmoBox = 138
	MissileSet = 144
	SupersonicMissileSet = 145
	GravityMissileSet = 146

	ElectromagneticMatrix = 9
	EnergyMatrix = 18
	StructureMatrix = 27
	InformationMatricx = 55
	GravityMatrix = 102
	UniverseMatrix = 75

	AntiMatter = 74  # "Mass-Energy Storage?!?"

	# Buildings
	WindTurbine = 7
	AssemblerI = 45
	AssemblerII = 46
	AssemblerIII = 47
	RayReceiver = 72
	SatelliteSubstation = 73,
	Accumulator = 76
	EnergyExchange = 77
	VerticalLaunchingSilo = 82
	BeltI = 84
	BeltII = 89
	BeltIII = 92
	SorterI = 85
	SorterII = 88
	SorterIII = 90
	StorageI = 86
	StorageII = 91
	StorageTank = 114
	Splitter = 87
	TrafficMonitor = 117
	LogisticsDistributor=122
	PlanetaryLogisticsStation = 93
	InterstellarLogisticsStation = 95
	Fractionator = 110
	OrbitalCollector = 111
	ChemicalPlant = 22
	QuantumChemicalPlant = 124
	SolarPanel=67
	ThermalPowerPlant=64
	MiniFusionPowerPlant = 113
	GeothermalPowerStation = 118
	ArtificialStar = 43
	ArcSmelter = 56
	PlaneSmelter = 116
	EmRailEjector = 71
	WaterPump = 49
	SprayCoater = 109
	MiniatureParticleCollider = 39
	MiningMachine = 48
	AdvancedMiningMachine = 119
	AutomaticPiler = 120
	MatrixLab = 10
	OilRefinery = 15
	WirelessPowerTower = 13
	OilExtractor = 14
	TeslaTower = 8


class ProductCategory(enum.Enum):
	ScienceMatrix = 'Science'
	Material = 'Materials'
	Component = 'Components'
	EndProduct = 'End Products'
	Smelted = 'Smelters'
	Proliferator = 'Proliferator'
	Ammo = 'Ammo'


class DysonSphereItem(enum.IntEnum):
	Lava = -1

	IronOre = 1001
	CopperOre = 1002
	SiliconOre = 1003
	TitaniumOre = 1004
	Stone = 1005
	Coal = 1006
	Log = 1030
	PlantFuel = 1031
	FireIce = 1011
	KimberliteOre = 1012
	FractalSilicon = 1013
	OpticalGratingCrystal = 1014
	SpiniformStalagmiteCrystal = 1015
	UnipolarMagnet = 1016
	IronIngot = 1101
	CopperIngot = 1104
	HighPuritySilicon = 1105
	TitaniumIngot = 1106
	StoneBrick = 1108
	EnergeticGraphite = 1109
	Steel = 1103
	TitaniumAlloy = 1107
	Glass = 1110
	TitaniumGlass = 1119
	Prism = 1111
	Diamond = 1112
	CrystalSilicon = 1113
	CombustibleUnit = 1128
	ExplosiveUnit = 1129
	CrystalExplosiveUnit = 1130
	Gear = 1201
	Magnet = 1102
	MagneticCoil = 1202
	ElectricMotor = 1203
	ElectromagneticTurbine = 1204
	SuperMagneticRing = 1205
	ParticleContainer = 1206
	StrangeMatter = 1127
	CircuitBoard = 1301
	Processor = 1303
	QuantumChip = 1305
	MicrocrystallineComponent = 1302
	PlaneFilter = 1304
	ParticleBroadband = 1402
	PlasmaExciter = 1401
	PhotonCombiner = 1404
	SolarSail = 1501
	Water = 1000
	CrudeOil = 1007
	RefinedOil = 1114
	SulfuricAcid = 1116
	Hydrogen = 1120
	Deuterium = 1121
	Antimatter = 1122
	CriticalPhoton = 1208
	HydrogenFuelRod = 1801
	DeuteronFuelRod = 1802
	AntimatterFuelRod = 1803
	Plastic = 1115
	Graphene = 1123
	CarbonNanotube = 1124
	OrganicCrystal = 1117
	TitaniumCrystal = 1118
	CasimirCrystal = 1126
	GravitonLens = 1209
	SpaceWarper = 1210
	AnnihilationConstraintSphere = 1403
	Thruster = 1405
	ReinforcedThruster = 1406
	LogisticsDrone = 5001
	LogisticsVessel = 5002
	FrameMaterial = 1125
	DysonSphereComponent = 1502
	SmallCarrierRocket = 1503
	Foundation = 1131
	ProliferatorMkI = 1141
	ProliferatorMkII = 1142
	ProliferatorMkIII = 1143
	MagnumAmmoBox = 1601
	TitaniumAmmoBox = 1602
	TitaniumAlloyAmmoBox = 1603
	MissileSet = 1609
	SupersonicMissileSet = 1610
	GravityMissileSet = 1611
	ConveyorBeltMKI = 2001
	ConveyorBeltMKII = 2002
	ConveyorBeltMKIII = 2003
	SorterMKI = 2011
	SorterMKII = 2012
	SorterMKIII = 2013
	Splitter = 2020
	TrafficMonitor = 2030
	AutomaticPiler = 2040
	StorageMKI = 2101
	StorageMKII = 2102
	StorageTank = 2106
	LogisticsDistributor = 2107
	AssemblingMachineMkI = 2303
	AssemblingMachineMkII = 2304
	AssemblingMachineMkIII = 2305
	PlaneSmelter = 2315
	TeslaTower = 2201
	WirelessPowerTower = 2202
	SatelliteSubstation = 2212
	WindTurbine = 2203
	ThermalPowerStation = 2204
	MiniFusionPowerStation = 2211
	MiningMachine = 2301
	ArcSmelter = 2302
	OilExtractor = 2307
	OilRefinery = 2308
	WaterPump = 2306
	ChemicalPlant = 2309
	Fractionator = 2314
	SprayCoater = 2313
	AdvancedMiningMachine = 2316
	QuantumChemicalPlant = 2317
	SolarPanel = 2205
	Accumulator = 2206
	AccumulatorFull = 2207
	EMRailEjector = 2311
	RayReceiver = 2208
	VerticalLaunchingSilo = 2312
	EnergyExchanger = 2209
	MiniatureParticleCollider = 2310
	ArtificialStar = 2210
	PlanetaryLogisticsStation = 2103
	InterstellarLogisticsStation = 2104
	OrbitalCollector = 2105
	MatrixLab = 2901
	MissileTurret = 3005
	SignalTower = 3007
	ShieldGenerator = 3008
	BattlefieldAnalysisBase = 3009
	ElectromagneticMatrix = 6001
	EnergyMatrix = 6002
	StructureMatrix = 6003
	InformationMatrix = 6004
	GravityMatrix = 6005
	UniverseMatrix = 6006

	# Unknown item ids; replace with correct values
	Engine = 98701

class LogisticsStationDirection(enum.IntEnum):
	Unused = 0
	Output = 1
	Input = 2

class ProliferationEffect(enum.IntEnum):
	Product = 0
	Speedup = 1

# Ideally, automatically generate this list from recipes or something
PRODUCTION_MACHINES = [
	DysonSphereItem.AssemblingMachineMkI,
	DysonSphereItem.AssemblingMachineMkII,
	DysonSphereItem.AssemblingMachineMkIII,
	DysonSphereItem.ChemicalPlant,
	DysonSphereItem.QuantumChemicalPlant,
	DysonSphereItem.ArcSmelter,
	DysonSphereItem.PlaneSmelter,
	DysonSphereItem.MatrixLab,
	DysonSphereItem.MiniatureParticleCollider,
	DysonSphereItem.OilRefinery,
	]
