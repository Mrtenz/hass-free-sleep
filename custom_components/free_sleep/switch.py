"""
Switch platform for Free Sleep Pod integration.

This module is loaded automatically by Home Assistant to set up switch entities
for the Free Sleep Pod integration.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from homeassistant.components.switch import (
  SwitchDeviceClass,
  SwitchEntity,
  SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
  DataUpdateCoordinator,
)

from .constants import DOMAIN
from .pod import Pod, Side


class SetValueFunction(Protocol):
  """Set value function protocol."""

  async def __call__(self, pod: Pod, value: bool) -> None:
    """
    Set the value for the pod.

    :param pod: The Free Sleep Pod instance.
    :param value: The value to set.
    :return: An awaitable that performs the action.
    """
    ...


@dataclass(frozen=True)
class FreeSleepSwitchDescription(SwitchEntityDescription):
  """A class that describes Free Sleep Pod switch entities."""

  on_icon: str | None = None
  off_icon: str | None = None

  get_value: Callable[[dict[str, Any]], bool] | None = None
  set_value: SetValueFunction | None = None


class SetSideValueFunction(Protocol):
  """Set value function protocol."""

  async def __call__(self, pod: Pod, side: Side, value: bool) -> None:
    """
    Set the value for the given side of the pod.

    :param pod: The Free Sleep Pod instance.
    :param side: The side of the pod.
    :param value: The value to set.
    :return: An awaitable that performs the action.
    """
    ...


@dataclass(frozen=True)
class FreeSleepSideSwitchDescription(FreeSleepSwitchDescription):
  """A class that describes Free Sleep Pod side switch entities."""

  set_value: SetSideValueFunction | None = None


POD_SWITCHES: tuple[FreeSleepSwitchDescription, ...] = (
  FreeSleepSwitchDescription(
    name='Prime Daily',
    key='prime_daily',
    translation_key='prime_daily',
    device_class=SwitchDeviceClass.SWITCH,
    on_icon='mdi:water-sync',
    off_icon='mdi:water-off',
    get_value=lambda data: data['settings']['primePodDaily']['enabled'],
    set_value=lambda pod, value: pod.set_prime_daily(value),
  ),
)

POD_SIDES_SWITCHES: tuple[FreeSleepSideSwitchDescription, ...] = (
  FreeSleepSideSwitchDescription(
    name='Away Mode',
    key='away_mode',
    translation_key='away_mode',
    device_class=SwitchDeviceClass.SWITCH,
    on_icon='mdi:home-outline',
    off_icon='mdi:home',
    get_value=lambda data: data['settings']['awayMode'],
    set_value=lambda _pod, side, value: side.set_away_mode(value),
  ),
)


async def async_setup_entry(
  hass: HomeAssistant,
  entry: ConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  """
  Set up switch entities for the Free Sleep Pod.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :param async_add_entities: Callback to add entities.
  """
  pod, coordinator = hass.data[DOMAIN][entry.entry_id]

  switches = [
    FreeSleepSwitch(coordinator, pod, description)
    for description in POD_SWITCHES
  ]

  async_add_entities(switches, update_before_add=True)

  for side in pod.sides:
    side_switches = [
      FreeSleepSideSwitch(coordinator, pod, side, description)
      for description in POD_SIDES_SWITCHES
    ]

    async_add_entities(side_switches, update_before_add=True)


class FreeSleepSwitch(CoordinatorEntity, SwitchEntity):
  """A class that represents a switch for a Free Sleep Pod."""

  entity_description: FreeSleepSwitchDescription

  _attr_has_entity_name = True

  def __init__(
    self,
    coordinator: DataUpdateCoordinator,
    pod: Pod,
    description: FreeSleepSwitchDescription,
  ) -> None:
    """
    Initialize the Free Sleep Pod switch entity.

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
  def is_on(self) -> bool:
    """Get whether the switch is on."""
    if self.entity_description.get_value:
      return self.entity_description.get_value(self.coordinator.data)

    return False

  @property
  def icon(self) -> str | None:
    """
    Get the icon for the switch entity based on its state.

    :return: The icon string.
    """
    if self.is_on and self.entity_description.on_icon:
      return self.entity_description.on_icon
    if not self.is_on and self.entity_description.off_icon:
      return self.entity_description.off_icon
    return super().icon

  async def async_turn_on(self) -> None:
    """Handle the switch turn on action."""
    if self.entity_description.set_value:
      await self.entity_description.set_value(self.pod, value=True)

  async def async_turn_off(self) -> None:
    """Handle the switch turn off action."""
    if self.entity_description.set_value:
      await self.entity_description.set_value(self.pod, value=False)


class FreeSleepSideSwitch(CoordinatorEntity, SwitchEntity):
  """A class that represents a switch for a Free Sleep Pod side."""

  entity_description: FreeSleepSwitchDescription

  _attr_has_entity_name = True

  def __init__(
    self,
    coordinator: DataUpdateCoordinator,
    pod: Pod,
    side: Side,
    description: FreeSleepSwitchDescription,
  ) -> None:
    """
    Initialize the Free Sleep Pod switch entity.

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
  def is_on(self) -> bool:
    """Get whether the switch is on."""
    if self.entity_description.get_value:
      return self.entity_description.get_value(
        self.side.get_side_data(self.coordinator.data)
      )

    return False

  @property
  def icon(self) -> str | None:
    """
    Get the icon for the switch entity based on its state.

    :return: The icon string.
    """
    if self.is_on and self.entity_description.on_icon:
      return self.entity_description.on_icon
    if not self.is_on and self.entity_description.off_icon:
      return self.entity_description.off_icon
    return super().icon

  async def async_turn_on(self) -> None:
    """Handle the switch turn on action."""
    if self.entity_description.set_value:
      await self.entity_description.set_value(self.pod, self.side, value=True)

  async def async_turn_off(self) -> None:
    """Handle the switch turn off action."""
    if self.entity_description.set_value:
      await self.entity_description.set_value(self.pod, self.side, value=False)
