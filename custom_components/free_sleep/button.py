"""
Button platform for Free Sleep Pod integration.

This module is loaded automatically by Home Assistant to set up button entities
for the Free Sleep Pod integration.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import (
  ButtonEntity,
  ButtonEntityDescription,
)
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
class FreeSleepButtonDescription(ButtonEntityDescription):
  """A class that describes Free Sleep Pod button entities."""

  name: str

  handle: Callable[[Pod], Awaitable[None]] | None = None
  """
  A callable that handles the button press action.

  :param pod: The Free Sleep Pod instance.
  :return: An awaitable that performs the action.
  """


POD_BUTTONS: tuple[FreeSleepButtonDescription, ...] = (
  FreeSleepButtonDescription(
    name='Prime',
    key='prime',
    translation_key='prime',
    icon='mdi:water-pump',
    handle=lambda pod: pod.prime(),
  ),
  FreeSleepButtonDescription(
    name='Reboot',
    key='reboot',
    translation_key='reboot',
    icon='mdi:restart',
    handle=lambda pod: pod.reboot(),
  ),
)


async def async_setup_entry(
  hass: HomeAssistant,
  entry: ConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  """
  Set up button entities for the Free Sleep pod.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :param async_add_entities: Callback to add entities.
  """
  pod, coordinator = hass.data[DOMAIN][entry.entry_id]
  buttons = [
    FreeSleepButton(coordinator, pod, description)
    for description in POD_BUTTONS
  ]

  async_add_entities(buttons, update_before_add=True)


class FreeSleepButton(CoordinatorEntity, ButtonEntity):
  """A class that represents a button for a Free Sleep Pod."""

  entity_description: FreeSleepButtonDescription

  _attr_has_entity_name = True

  def __init__(
    self,
    coordinator: DataUpdateCoordinator,
    pod: Pod,
    description: FreeSleepButtonDescription,
  ) -> None:
    """
    Initialize the Free Sleep button entity.

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

  async def async_press(self) -> None:
    """Handle the button press action."""
    if self.entity_description.handle:
      await self.entity_description.handle(self.pod)
