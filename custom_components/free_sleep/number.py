"""
Number platform for Free Sleep Pod integration.

This module is loaded automatically by Home Assistant to set up number entities
for the Free Sleep Pod integration.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
  NumberEntity,
  NumberEntityDescription,
  NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
  PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
  DataUpdateCoordinator,
)

from .constants import DOMAIN
from .pod import Pod


@dataclass(frozen=True)
class FreeSleepNumberDescription(NumberEntityDescription):
  """A class that describes Free Sleep Pod number entities."""

  get_value: Callable[[dict[str, Any]], StateType] | None = None
  set_value: Callable[[Pod, StateType], Awaitable[None]] | None = None


POD_SENSORS: tuple[FreeSleepNumberDescription, ...] = (
  FreeSleepNumberDescription(
    name='LED Brightness',
    key='led_brightness',
    translation_key='led_brightness',
    mode=NumberMode.SLIDER,
    native_min_value=0,
    native_max_value=100,
    native_step=1,
    native_unit_of_measurement=PERCENTAGE,
    get_value=lambda data: data['status']['settings']['ledBrightness'],
    set_value=lambda pod, value: pod.set_led_brightness(int(value)),
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
  numbers = [
    FreeSleepNumber(coordinator, pod, description)
    for description in POD_SENSORS
  ]

  async_add_entities(numbers, update_before_add=True)


class FreeSleepNumber(CoordinatorEntity, NumberEntity):
  """A class that represents a number for a Free Sleep Pod."""

  entity_description: FreeSleepNumberDescription

  _attr_has_entity_name = True

  def __init__(
    self,
    coordinator: DataUpdateCoordinator,
    pod: Pod,
    description: FreeSleepNumberDescription,
  ) -> None:
    """
    Initialize the Free Sleep Pod number entity.

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
  def native_value(self) -> StateType:
    """
    Return the current value of the number entity.

    :return: The current value.
    """
    if self.entity_description.get_value:
      return self.entity_description.get_value(self.coordinator.data)

    return None

  async def async_set_native_value(self, value: float) -> None:
    """
    Set the value of the number entity.

    :param value: The new value to set.
    """
    if self.entity_description.set_value:
      await self.entity_description.set_value(self.pod, value)

    await self.coordinator.async_request_refresh()
