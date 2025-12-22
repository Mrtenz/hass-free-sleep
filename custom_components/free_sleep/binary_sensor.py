"""
Binary sensor platform for Free Sleep Pod integration.

This module is loaded automatically by Home Assistant to set up binary sensor
entities for the Free Sleep Pod integration.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
  BinarySensorEntity,
  BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from sensor_state_data import BinarySensorDeviceClass

from . import FreeSleepCoordinator
from .constants import DOMAIN
from .pod import Pod, Side


@dataclass(frozen=True)
class FreeSleepBinarySensorDescription(BinarySensorEntityDescription):
  """A class that describes Free Sleep Pod binary sensor entities."""

  name: str
  device_class: BinarySensorDeviceClass
  icon_on: str | None = None
  icon_off: str | None = None

  get_value: Callable[[dict[str, Any]], bool] | None = None


POD_BINARY_SENSORS: tuple[FreeSleepBinarySensorDescription, ...] = (
  FreeSleepBinarySensorDescription(
    name='Priming',
    key='priming',
    translation_key='priming',
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_on='mdi:water-pump',
    icon_off='mdi:water-pump-off',
    get_value=lambda data: data['status']['isPriming'],
  ),
  FreeSleepBinarySensorDescription(
    name='Water Level',
    key='water_level',
    translation_key='water_level',
    device_class=BinarySensorDeviceClass.PROBLEM,
    icon_on='mdi:water-remove',
    icon_off='mdi:water-check',
    get_value=lambda data: not data['status']['waterLevel'],
  ),
)


@dataclass(frozen=True)
class FreeSleepSideBinarySensorDescription(BinarySensorEntityDescription):
  """A class that describes Free Sleep Pod side binary sensor entities."""

  name: str
  device_class: BinarySensorDeviceClass
  icon_on: str | None = None
  icon_off: str | None = None

  get_value: Callable[[dict[str, Any]], bool] | None = None


POD_SIDE_BINARY_SENSORS: tuple[FreeSleepSideBinarySensorDescription, ...] = (
  FreeSleepSideBinarySensorDescription(
    name='Presence',
    key='bed_presence',
    translation_key='presence',
    device_class=BinarySensorDeviceClass.OCCUPANCY,
    icon_on='mdi:bed',
    icon_off='mdi:bed-empty',
    get_value=lambda data: data['presence']['present'],
  ),
)


async def async_setup_entry(
  hass: HomeAssistant,
  entry: ConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  """
  Set up sensor entities for the Free Sleep pod.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :param async_add_entities: Callback to add entities.
  """
  pod, coordinator = hass.data[DOMAIN][entry.entry_id]
  binary_sensors = [
    FreeSleepBinarySensor(coordinator, pod, description)
    for description in POD_BINARY_SENSORS
  ]

  async_add_entities(binary_sensors, update_before_add=True)

  for side in pod.sides:
    side_binary_sensors = [
      FreeSleepSideBinarySensor(coordinator, pod, side, description)
      for description in POD_SIDE_BINARY_SENSORS
    ]

    async_add_entities(side_binary_sensors, update_before_add=True)


class FreeSleepBinarySensor(
  CoordinatorEntity[FreeSleepCoordinator], BinarySensorEntity
):
  """A class that represents a sensor for a Free Sleep Pod."""

  entity_description: FreeSleepBinarySensorDescription

  _attr_has_entity_name = True

  def __init__(
    self,
    coordinator: FreeSleepCoordinator,
    pod: Pod,
    description: FreeSleepBinarySensorDescription,
  ) -> None:
    """
    Initialize the Free Sleep binary sensor entity.

    :param coordinator: The data update coordinator.
    :param pod: The Free Sleep Pod instance.
    :param description: The entity description.
    """
    super().__init__(coordinator)

    self.pod = pod
    self.entity_description = description
    self._attr_name = description.name
    self._attr_unique_id = f'{pod.id}_{description.key}'

  @property
  def device_info(self) -> dict:
    """
    Return device information for the Free Sleep Pod. This is used by Home
    Assistant to group entities under a single device.

    :return: A dictionary containing device information.
    """
    return self.pod.device_info

  @property
  def is_on(self) -> bool | None:
    """
    Get whether the binary sensor is on.

    :return: True if the sensor is on, False otherwise.
    """
    if self.entity_description.get_value:
      return self.entity_description.get_value(self.coordinator.data)

    return None

  @property
  def icon(self) -> str | None:
    """
    Get the icon for the binary sensor based on its state.

    :return: The icon string.
    """
    if self.is_on and self.entity_description.icon_on:
      return self.entity_description.icon_on
    if not self.is_on and self.entity_description.icon_off:
      return self.entity_description.icon_off
    return super().icon


class FreeSleepSideBinarySensor(
  CoordinatorEntity[FreeSleepCoordinator], BinarySensorEntity
):
  """A class that represents a binary sensor for a Free Sleep Pod side."""

  entity_description: FreeSleepSideBinarySensorDescription

  _attr_has_entity_name = True

  def __init__(
    self,
    coordinator: FreeSleepCoordinator,
    pod: Pod,
    side: Side,
    description: FreeSleepSideBinarySensorDescription,
  ) -> None:
    """
    Initialize the Free Sleep side binary sensor entity.

    :param coordinator: The data update coordinator.
    :param pod: The Free Sleep Pod instance.
    :param side: The side of the pod (left or right).
    :param description: The entity description.
    """
    super().__init__(coordinator)

    self.pod = pod
    self.side = side
    self.entity_description = description
    self._attr_name = description.name
    self._attr_unique_id = f'{side.id}_{description.key}'

  @property
  def device_info(self) -> dict:
    """
    Return device information for the Free Sleep Pod. This is used by Home
    Assistant to group entities under a single device.

    :return: A dictionary containing device information.
    """
    return self.side.device_info

  @property
  def is_on(self) -> bool | None:
    """
    Get whether the binary sensor is on.

    :return: True if the sensor is on, False otherwise.
    """
    if self.entity_description.get_value:
      data = self.side.get_side_data(self.coordinator.data)
      return self.entity_description.get_value(data)

    return None

  @property
  def icon(self) -> str | None:
    """
    Get the icon for the binary sensor based on its state.

    :return: The icon string.
    """
    if self.is_on and self.entity_description.icon_on:
      return self.entity_description.icon_on
    if not self.is_on and self.entity_description.icon_off:
      return self.entity_description.icon_off
    return super().icon
