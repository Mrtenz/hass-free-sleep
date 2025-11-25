"""
Time platform for Free Sleep Pod integration.

This module is loaded automatically by Home Assistant to set up time entities
for the Free Sleep Pod integration.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import time
from typing import Any

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
  DataUpdateCoordinator,
)

from .constants import DOMAIN
from .pod import Pod


@dataclass(frozen=True)
class FreeSleepTimeDescription(TimeEntityDescription):
  """A class that describes Free Sleep Pod time entities."""

  get_value: Callable[[dict[str, Any]], str | time] | None = None
  set_value: Callable[[Pod, str], Awaitable[None]] | None = None


POD_TIMES: tuple[FreeSleepTimeDescription, ...] = (
  FreeSleepTimeDescription(
    name='Prime Daily Time',
    key='prime_daily_time',
    translation_key='prime_daily_time',
    get_value=lambda data: data['settings']['primePodDaily']['time'],
    set_value=lambda pod, value: pod.set_prime_daily_time(value),
  ),
)


async def async_setup_entry(
  hass: HomeAssistant,
  entry: ConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  """
  Set up time entities for the Free Sleep pod.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :param async_add_entities: Callback to add entities.
  """
  pod, coordinator = hass.data[DOMAIN][entry.entry_id]

  side_switches = [
    FreeSleepTime(coordinator, pod, description) for description in POD_TIMES
  ]

  async_add_entities(side_switches, update_before_add=True)


class FreeSleepTime(CoordinatorEntity, TimeEntity):
  """A class that represents a time for a Free Sleep Pod."""

  entity_description: FreeSleepTimeDescription

  _attr_has_entity_name = True

  def __init__(
    self,
    coordinator: DataUpdateCoordinator,
    pod: Pod,
    description: FreeSleepTimeDescription,
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
  def native_value(self) -> time | None:
    """
    Return the current value of the time entity.

    :return: The current value.
    """
    if self.entity_description.get_value:
      value = self.entity_description.get_value(self.coordinator.data)
      if isinstance(value, time):
        return value

      hour, minute = map(int, value.split(':'))
      return time(hour=hour, minute=minute)

    return None

  async def async_set_value(self, value: time) -> None:
    """
    Set the value of the time entity.

    :param value: The new value to set.
    """
    if self.entity_description.set_value:
      time_string = value.strftime('%H:%M')
      await self.entity_description.set_value(self.pod, time_string)

    await self.coordinator.async_request_refresh()
