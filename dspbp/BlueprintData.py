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

import collections
import enum

from .NamedStruct import NamedStruct
from .Enums import DysonSphereItem, LogisticsStationDirection, ProliferationEffect
from .Enums import DysonSphereItem as dsi, PRODUCTION_MACHINES

PLANETARY_LOGISTICS_STATION_STORAGE_SIZE = 4
INTERSTELLAR_LOGISTICS_STATION_STORAGE_SIZE = 5
CONVEYORS = [dsi.ConveyorBeltMKI, dsi.ConveyorBeltMKII, dsi.ConveyorBeltMKIII]

class ParameterType(enum.StrEnum):
	CONVEYOR = 'conveyer'
	PRODUCTION = 'production'
	STATION = 'station'
	UNKNOWN = 'unknown'

class CustomizedParameters():
	SENTINEL = ParameterType.UNKNOWN
	"""
	Base class for buildings with understood parameters which allows them to be reconstructed.
	"""
	def __init__(self, parameters):
		self._raw_parameters = parameters

	@property
	def raw_parameters(self):
		"""
		Returns a copy of the raw parameters for this instance, updated with any value changes
		"""
		parameters = list(self._raw_parameters)
		for index, value in self._encode_parameter_map.items():
			value = (1 if value else 0) if isinstance(value, bool) else value
			if not isinstance(value, int):
				raise ValueError(f'Unable to convert {value} parameter (index={index} for {self}')
			parameters[index] = value
		return parameters

	@property
	def _encode_parameter_map(self):
		"""
		Returns a map of parameter index to values. Any missing parameters will use their original value.
		"""
		if not hasattr(self, '_PARAMETER_KEY_OFFSETS') or not hasattr(self, '_PARAMETERS_OFFSET'):
			raise NotImplementedError(f'{self.__class__} unable to map parameter to original indices')
		# For most parameters, this simple approach is sufficient
		mapping = {}
		for key, offset in self._PARAMETER_KEY_OFFSET.items():
			mapping[self._PARAMETERS_OFFSET + offset] = getattr(self.parameters, key)
		return mapping



class LogisticsDistributorParameters(CustomizedParameters):
	_Parameters = collections.namedtuple('Parameters', [ "supply_icarus_logic", "supply_logic", "work_energy", "autofill"])
	_PARAMETER_KEY_OFFSETS = {
		'supply_icarus_logic' : 0,
		'supply_logic' : 1,
		'work_energy' : 2,
		'autofill' : 3,
	}

	__PARAMETER_CONVERTERS = {
		'supply_logic' : LogisticsStationDirection
	}

	def __init__(self, parameters):
		super().__init__(parameters)
		self._parameters = self._Parameters(**{
			key :
				self.__PARAMETER_CONVERTERS.get(key, lambda x: x)(parameters[offset]) for key, offset in self._PARAMETER_KEY_OFFSETS.items()
		})

	@property
	def parameters(self):
		return self._parameters

class ConveyorBeltParameters(CustomizedParameters):
	SENTINEL = ParameterType.CONVEYOR
	_Parameters = collections.namedtuple('Parameters', ['memo_icon', 'memo_number'])
	_PARAMETERS_OFFSET = 0
	_PARAMETER_KEY_OFFSETS = {
		'memo_icon' : 0,
		'memo_number' : 1,
	}

	def __init__(self, parameters):
		super().__init__(parameters)
		if parameters:
			self._parameters = self._Parameters(**{
				key : parameters[offset] for key, offset in self._PARAMETER_KEY_OFFSETS.items()
			})
		else:
			self._parameters = None

	@property
	def parameters(self):
		return self._parameters


class ProductionBuildingParameters(CustomizedParameters):
	SENTINEL = ParameterType.PRODUCTION
	_Parameters = collections.namedtuple('Parameters', [ 'proliferation_effect'])

	_PARAMETERS_OFFSET = 0
	_PARAMETER_KEY_OFFSETS = {
		'proliferation_effect' : 0,
	}
	_PARAMETER_CONVERTERS = {
		'proliferation_effect' : ProliferationEffect
	}
	def __init__(self, parameters):
		super().__init__(parameters)
		self._parameters = self._Parameters(**{
			key : self._PARAMETER_CONVERTERS.get(key, lambda x: x)(parameters[offset]) for key, offset in self._PARAMETER_KEY_OFFSETS.items()
		})

	@property
	def parameters(self):
		return self._parameters

	def to_dict(self):
		return self.parameters._asdict()

class StationParameters(CustomizedParameters):
	SENTINEL = ParameterType.STATION
	_Parameters = collections.namedtuple("Parameters", [ "work_energy", "drone_range", "vessel_range", "orbital_collector", "warp_distance", "equip_warper", "drone_count", "vessel_count" ])
	_STORAGE_OFFSET = 0
	_SLOTS_OFFSET = _STORAGE_OFFSET + 192
	_PARAMETERS_OFFSET = _SLOTS_OFFSET + 128

	_STORAGE_KEY_OFFSETS = {
		'item_id' : 0,
		'local_logic' : 1,
		'remote_logic' : 2,
		'max_count' : 3
	}

	_SLOT_KEY_OFFSETS = {
		'direction': 0,
		'storage_index' : 1
	}

	_PARAMETER_KEY_OFFSETS = {
		'work_energy': 0,
		'drone_range': 1,
		'vessel_range': 2,
		'orbital_collector': 3,
		'warp_distance': 4,
		'equip_warper': 5,
		'drone_count': 6,
		'vessel_count': 7,
	}

	def __init__(self, parameters, storage_len, slots_len):
		super().__init__(parameters)
		self._storage = self._parse_storage(parameters, storage_len)
		self._slots = self._parse_slots(parameters, slots_len)
		self._parameters = self._parse_parameters(parameters)
		self._raw_parameters = parameters

	@property
	def storage(self):
		return self._storage

	@property
	def slots(self):
		return self._slots

	@property
	def parameters(self):
		return self._parameters

	@property
	def _encode_parameter_map(self):
		mapping = {}
		for ix, storage in enumerate(self.storage):
			storage_offset = self._STORAGE_OFFSET + (6 * ix)
			for key, offset in self._STORAGE_KEY_OFFSETS.items():
				mapping[storage_offset + offset] = storage[key] if storage else 0
		for ix, slot in enumerate(self.slots):
			slot_offset  = self._SLOTS_OFFSET + (4 * ix)
			for key, offset in self._SLOT_KEY_OFFSETS.items():
				original_value = self._raw_parameters[slot_offset + offset]
				mapping[slot_offset + offset] = slot[key] if slot else original_value
		for key, offset in self._PARAMETER_KEY_OFFSETS.items():
			mapping[self._PARAMETERS_OFFSET + offset] = getattr(self.parameters, key)
		return mapping

	def _parse_storage(self, parameters, storage_len):
		storage = [ ]
		for offset in range(self._STORAGE_OFFSET, self._STORAGE_OFFSET + (6 * storage_len), 6):
			item_id = parameters[offset + 0]
			if item_id == 0:
				# Storage unused
				storage.append(None)
			else:
				storage.append({
					"item_id": parameters[offset + 0],
					"local_logic": parameters[offset + 1],
					"remote_logic": parameters[offset + 2],
					"max_count": parameters[offset + 3],
				})
		return storage

	def _parse_slots(self, parameters, slots_len):
		slots = [ ]
		for offset in range(self._SLOTS_OFFSET, self._SLOTS_OFFSET + (4 * slots_len), 4):
			storage_index = parameters[offset + 1]
			if storage_index == 0:
				# Slot unused
				slots.append(None)
			else:
				slots.append({
					"direction": LogisticsStationDirection(parameters[offset + 0]),
					"storage_index": parameters[offset + 1],
				})
		return slots

	def _parse_parameters(self, parameters):
		args = {
			"work_energy": parameters[self._PARAMETERS_OFFSET + 0],
			"drone_range": parameters[self._PARAMETERS_OFFSET + 1],
			"vessel_range": parameters[self._PARAMETERS_OFFSET + 2],
			"orbital_collector": (parameters[self._PARAMETERS_OFFSET + 3] == 1),
			"warp_distance": parameters[self._PARAMETERS_OFFSET + 4],
			"equip_warper":  (parameters[self._PARAMETERS_OFFSET + 5] == 1),
			"drone_count": parameters[self._PARAMETERS_OFFSET + 6],
			"vessel_count":  parameters[self._PARAMETERS_OFFSET + 7],
		}
		return self._Parameters(**args)

	def to_dict(self):
		return {
			"storage": self._storage,
			"slots": self._slots,
			"parameters": self._parameters._asdict(),
		}

class BlueprintArea():
	_BLUEPRINT_AREA = NamedStruct((
		("b", "index"),
		("b", "parent_index"),
		("H", "tropic_anchor"),
		("H", "area_segments"),
		("H", "anchor_local_offset_x"),
		("H", "anchor_local_offset_y"),
		("H", "width"),
		("H", "height"),
	))

	def __init__(self, fields):
		self._fields = fields

	@property
	def size(self):
		return self._BLUEPRINT_AREA.size

	def to_dict(self):
		return self._fields._asdict()

	def pack(self):
		return self._BLUEPRINT_AREA.pack(self._fields._asdict())

	def __str__(self):
		return f'<area {self._fields.parent_index}.{self._fields.index}: {self._fields.width}x{self._fields.height} {self._fields.area_segments} segments, tropic {self._fields.tropic_anchor}>'

	@classmethod
	def deserialize(cls, data, offset):
		fields = cls._BLUEPRINT_AREA.unpack_head(data, offset)
		return cls(fields)

class BlueprintBuilding():
	_BLUEPRINT_BUILDING = NamedStruct((
		("L", "index"),
		("b", "area_index"),
		("f", "local_offset_x"),
		("f", "local_offset_y"),
		("f", "local_offset_z"),
		("f", "local_offset_x2"),
		("f", "local_offset_y2"),
		("f", "local_offset_z2"),
		("f", "yaw"),
		("f", "yaw2"),
		("H", "item_id"),
		("H", "model_index"),
		("L", "output_object_index"),
		("L", "input_object_index"),
		("b", "output_to_slot"),
		("b", "input_from_slot"),
		("b", "output_from_slot"),
		("b", "input_to_slot"),
		("b", "output_offset"),
		("b", "input_offset"),
		("H", "recipe_id"),
		("H", "filter_id"),
		("H", "parameter_count"),
	))

	def __init__(self, fields, parameters):
		self._fields = fields
		self._parameters = parameters

	@property
	def item(self):
		try:
			return DysonSphereItem(self._fields.item_id)
		except ValueError:
			return None

	@property
	def data(self):
		return self._fields

	@property
	def raw_parameters(self):
		return self._parameters

	@property
	def parameters(self):
		if self.item == DysonSphereItem.PlanetaryLogisticsStation:
			return StationParameters(self._parameters, storage_len = PLANETARY_LOGISTICS_STATION_STORAGE_SIZE, slots_len = 12)
		elif self.item == DysonSphereItem.InterstellarLogisticsStation:
			return StationParameters(self._parameters, storage_len = INTERSTELLAR_LOGISTICS_STATION_STORAGE_SIZE, slots_len = 12)
		elif self.item == DysonSphereItem.LogisticsDistributor:
			return LogisticsDistributorParameters(self._parameters)
		elif self.item in PRODUCTION_MACHINES:
			return ProductionBuildingParameters(self._parameters)
		elif self.item in CONVEYORS:
			return ConveyorBeltParameters(self._parameters)
		return self._parameters

	@property
	def size(self):
		return self._BLUEPRINT_BUILDING.size + (len(self._parameters) * 4)

	def to_dict(self):
		result = self._fields._asdict()
		if self.item is not None:
			result["item_id"] = self.item.name
		result["parameters"] = self.parameters
		if not isinstance(result["parameters"], list):
			result["parameters"] = result["parameters"].to_dict()
		return result

	def pack(self):
		raw_parameters = self.raw_parameters
		try:
			raw_parameters = self.parameters.raw_parameters
		except AttributeError:
			pass
		if len(raw_parameters) != self._fields.parameter_count:
			raise  ValueError("Parameter length mismatch")
		return self._BLUEPRINT_BUILDING.pack(self._fields._asdict()) + b''.join([value.to_bytes(length=4, byteorder='little') for value in raw_parameters])

	@classmethod
	def deserialize(cls, data, offset):
		fields = cls._BLUEPRINT_BUILDING.unpack_head(data, offset)
		offset += cls._BLUEPRINT_BUILDING.size

		parameters = [ int.from_bytes(data[offset + 4 * i : offset + (4 * (i + 1)) ], byteorder = "little") for i in range(fields.parameter_count) ]
		return cls(fields, parameters)

class BlueprintData():
	_HEADER = NamedStruct((
		("L", "version"),
		("L", "cursor_offset_x"),
		("L", "cursor_offset_y"),
		("L", "cursor_target_area"),
		("L", "dragbox_size_x"),
		("L", "dragbox_size_y"),
		("L", "primary_area_index"),
		("B", "area_count"),
	))
	_BUILDING_HEADER = NamedStruct((
		("L", "building_count"),
	))

	def __init__(self, header, areas, buildings):
		self._header = header
		self._areas = areas
		self._buildings = buildings

	@property
	def buildings(self):
		return self._buildings

	def to_dict(self):
		result = self._header._asdict()
		result["areas"] = [ area.to_dict() for area in self._areas ]
		result["buildings"] = [ building.to_dict() for building in self._buildings ]
		return result

	def serialize(self):
		serialized_data = b''.join(
			[self._HEADER.pack(self._header._asdict())] +
			[area.pack() for area in self._areas] +
			[self._BUILDING_HEADER.pack({'building_count' : len(self._buildings)})] +
			[building.pack() for building in self._buildings])
		return serialized_data

	@classmethod
	def deserialize(cls, data):
		header = cls._HEADER.unpack_head(data)

		areas = [ ]
		offset = cls._HEADER.size

		for area_id in range(header.area_count):
			area = BlueprintArea.deserialize(data, offset)
			offset += area.size
			areas.append(area)

		buildings = [ ]
		building_header = cls._BUILDING_HEADER.unpack_head(data, offset)
		offset += cls._BUILDING_HEADER.size
		for building_id in range(building_header.building_count):
			building = BlueprintBuilding.deserialize(data, offset)
			offset += building.size
			buildings.append(building)

		if len(data) != offset:
			print(f'Data length is {len(data)} but {offset} bytes deserialized.')

		return cls(header, areas, buildings)
