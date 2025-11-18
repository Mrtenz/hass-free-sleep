"""
Climate platform for Free Sleep integration.

This module is loaded automatically by Home Assistant to set up climate entities
for the Free Sleep integration.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.climate import (
  ClimateEntity,
  ClimateEntityDescription,
  HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
  DataUpdateCoordinator,
)

from .constants import (
  DOMAIN,
  EIGHT_SLEEP_MAX_TEMPERATURE_F,
  EIGHT_SLEEP_MIN_TEMPERATURE_F,
  EIGHT_SLEEP_TEMPERATURE_STEP_F,
)
from .pod import Pod, Side


@dataclass(frozen=True)
class FreeSleepClimateDescription(ClimateEntityDescription):
  """A class that describes a Free Sleep Pod climate entity."""

  get_current_temperature: Callable[[dict[str, Any]], float] | None = None
  get_target_temperature: Callable[[dict[str, Any]], float] | None = None


POD_SIDE_CLIMATES: tuple[FreeSleepClimateDescription, ...] = (
  FreeSleepClimateDescription(
    name='Temperature',
    key='temperature',
    translation_key='temperature',
    icon='mdi:water-thermometer',
    get_current_temperature=lambda data: data['status']['currentTemperatureF'],
    get_target_temperature=lambda side: side['status']['targetTemperatureF'],
  ),
)


async def async_setup_entry(
  hass: HomeAssistant,
  entry: ConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  """
  Set up climate entities for the Free Sleep pod side.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :param async_add_entities: Callback to add entities.
  """
  pod, coordinator = hass.data[DOMAIN][entry.entry_id]

  for side in pod.sides:
    side_switches = [
      FreeSleepSideClimate(coordinator, pod, side, description)
      for description in POD_SIDE_CLIMATES
    ]

    async_add_entities(side_switches, update_before_add=True)


class FreeSleepSideClimate(
  CoordinatorEntity,
  ClimateEntity,
):
  """A class that represents a Free Sleep Pod side climate entity."""

  entity_description: FreeSleepClimateDescription

  _attr_has_entity_name: Final = True
  _attr_temperature_unit: Final = UnitOfTemperature.FAHRENHEIT
  _attr_hvac_modes: Final = [HVACMode.HEAT_COOL, HVACMode.OFF]
  _attr_min_temp: Final = EIGHT_SLEEP_MIN_TEMPERATURE_F
  _attr_max_temp: Final = EIGHT_SLEEP_MAX_TEMPERATURE_F
  _attr_target_temperature_step: Final = EIGHT_SLEEP_TEMPERATURE_STEP_F

  def __init__(
    self,
    coordinator: DataUpdateCoordinator,
    pod: Pod,
    side: Side,
    description: FreeSleepClimateDescription,
  ) -> None:
    """
    Initialize the Free Sleep Pod side climate entity.

    :param coordinator: The data update coordinator.
    :param pod: The Free Sleep Pod instance.
    :param side: The side of the pod (left or right).
    :param description: The climate entity description.
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
  def current_temperature(self) -> float | None:
    """Return the current temperature."""
    if self.entity_description.get_current_temperature:
      return self.entity_description.get_current_temperature(
        self.side.get_side_data(self.coordinator.data)
      )
    return None

  @property
  def target_temperature(self) -> float | None:
    """Return the target temperature."""
    if self.entity_description.get_target_temperature:
      return self.entity_description.get_target_temperature(
        self.side.get_side_data(self.coordinator.data)
      )
    return None

  @property
  def hvac_mode(self) -> HVACMode:
    """
    Get the current HVAC mode.

    :return: The current HVAC mode.
    """
    if self.side.get_side_data(self.coordinator.data)['status']['isOn']:
      return HVACMode.HEAT_COOL

    return HVACMode.OFF

  async def async_set_temperature(self, **kwargs: float) -> None:
    """
    Set the target temperature.

    :param kwargs: The keyword arguments containing the target temperature.
    """
    temperature = kwargs.get('temperature')
    if temperature is not None:
      await self.side.set_target_temperature(float(temperature))

  async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
    """
    Set the HVAC mode.

    :param hvac_mode: The desired HVAC mode.
    """
    if hvac_mode == HVACMode.OFF:
      await self.side.set_active(False)
    else:
      await self.side.set_active(True)
