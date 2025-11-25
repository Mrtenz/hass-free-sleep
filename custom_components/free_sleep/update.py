"""
Update platform for Free Sleep Pod integration.

This module is loaded automatically by Home Assistant to set up update entities
for the Free Sleep Pod integration.
"""

from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .constants import DOMAIN
from .coordinator import FirmwareUpdateCoordinator
from .logger import log
from .pod import Pod


async def async_setup_entry(
  hass: HomeAssistant,
  entry: ConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  """
  Set up update entities for the Free Sleep pod.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :param async_add_entities: Callback to add entities.
  """
  pod, _coordinator = hass.data[DOMAIN][entry.entry_id]
  firmware_coordinator = FirmwareUpdateCoordinator(hass, log, pod.api)

  async_add_entities(
    [FreeSleepUpdate(firmware_coordinator, pod)], update_before_add=True
  )


class FreeSleepUpdate(CoordinatorEntity, UpdateEntity):
  """Update entity for Free Sleep Pod firmware updates."""

  _attr_has_entity_name = True
  _attr_name = 'Firmware'
  _attr_translation_key = 'firmware'
  _attr_supported_features = UpdateEntityFeature.INSTALL

  def __init__(self, coordinator: FirmwareUpdateCoordinator, pod: Pod) -> None:
    """
    Initialize the Free Sleep Update entity.

    :param coordinator: The data update coordinator.
    :param pod: The Free Sleep Pod instance.
    """
    super().__init__(coordinator)
    self.pod = pod
    self._attr_unique_id = f'{pod.id}_firmware'

  @property
  def device_info(self) -> dict:
    """
    Return device information for the Free Sleep Pod.

    This is used by Home Assistant to group entities under a single device.

    :return: A dictionary containing device information.
    """
    return self.pod.device_info

  @property
  def installed_version(self) -> str | None:
    """
    Return the currently installed firmware version.

    :return: The installed firmware version.
    """
    return self.coordinator.data.get('current_version')

  @property
  def latest_version(self) -> str | None:
    """
    Return the latest available firmware version.

    :return: The latest firmware version.
    """
    return self.coordinator.data.get('latest_version')

  async def async_install(self, **_kwargs: dict[str, Any]) -> None:
    """Install the latest firmware update."""
    await self.pod.api.run_jobs(['update'])
