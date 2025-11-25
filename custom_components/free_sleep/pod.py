"""Classes to represent a Free Sleep Pod device and its sides."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FreeSleepAPI
from .constants import PodSide
from .coordinator import PodState


class Pod:
  """A class that represents a Free Sleep Pod device."""

  manufacturer: str = 'Eight Sleep'

  host: str

  def __init__(
    self,
    hass: HomeAssistant,
    coordinator: DataUpdateCoordinator[PodState],
    entry: ConfigEntry,
    name: str,
    host: str,
  ) -> None:
    """
    Initialize the Free Sleep Pod device.

    :param hass: The Home Assistant instance.
    :param coordinator: The data update coordinator for the pod.
    :param entry: The configuration entry.
    :param name: The name of the Free Sleep Pod device. This should be fetched
    from the device during setup.
    :param host: The host address of the Free Sleep Pod device.
    """
    self.hass = hass
    self.coordinator = coordinator
    self.api = FreeSleepAPI(host, async_get_clientsession(hass))

    self.id = entry.entry_id
    self.model: str = name
    self.host = host
    self.name = name
    self.sides = [
      Side(hass, coordinator, self, 'left'),
      Side(hass, coordinator, self, 'right'),
    ]

  @property
  def device_info(self) -> dict:
    """
    Return device information for the Free Sleep Pod. This is used by Home
    Assistant to group entities under a single device.

    :return: A dictionary containing device information.
    """
    return {
      'identifiers': {(self.manufacturer, self.id)},
      'name': self.name,
      'manufacturer': self.manufacturer,
      'model': self.model,
    }

  async def set_prime_daily(self, enabled: bool) -> None:
    """
    Enable or disable daily priming for the Free Sleep Pod device.

    :param enabled: True to enable daily priming, False to disable.
    """
    json_data = {'primePodDaily': {'enabled': enabled}}
    await self.api.update_settings(json_data)

    data = self.coordinator.data
    data['settings']['primePodDaily']['enabled'] = enabled
    self.coordinator.async_set_updated_data(data)

  async def set_reboot_daily(self, enabled: bool) -> None:
    """
    Enable or disable daily rebooting for the Free Sleep Pod device.

    :param enabled: True to enable daily rebooting, False to disable.
    """
    json_data = {'rebootDaily': enabled}
    await self.api.update_settings(json_data)

    data = self.coordinator.data
    data['settings']['rebootDaily'] = enabled
    self.coordinator.async_set_updated_data(data)

  async def set_led_brightness(self, brightness: int) -> None:
    """
    Set the LED brightness for the Free Sleep Pod device.

    :param brightness: The desired brightness level (0-100).
    """
    json_data = {'settings': {'ledBrightness': brightness}}
    await self.api.update_device_status(json_data)

    data = self.coordinator.data
    data['status']['settings']['ledBrightness'] = brightness
    self.coordinator.async_set_updated_data(data)

  async def reboot(self) -> None:
    """Reboot the Free Sleep Pod device."""
    await self.api.run_jobs(['reboot'])


class Side:
  """A class that represents a side of a Free Sleep Pod device."""

  def __init__(
    self,
    hass: HomeAssistant,
    coordinator: DataUpdateCoordinator[PodState],
    pod: Pod,
    side: PodSide,
  ) -> None:
    """
    Initialize the Free Sleep Pod side.

    :param hass: The Home Assistant instance.
    :param coordinator: The data update coordinator for the pod.
    :param pod: The Free Sleep Pod instance.
    :param side: The side of the pod ('left' or 'right').
    """
    self.hass = hass
    self.coordinator = coordinator
    self.pod = pod
    self.type = side
    self.id = f'{pod.id}_{side}'
    self.name = f'{pod.model} {side.capitalize()}'

  @property
  def device_info(self) -> dict:
    """
    Return device information for the Free Sleep Pod. This is used by Home
    Assistant to group entities under a single device.

    :return: A dictionary containing device information.
    """
    return {
      'identifiers': {(self.pod.manufacturer, self.id)},
      'name': self.name,
      'manufacturer': self.pod.manufacturer,
      'model': self.pod.model,
    }

  def get_side_data(self, data: PodState) -> dict[str, Any]:
    """
    Get the data for this side of the Free Sleep Pod device.

    :param data: The complete pod state data.
    :return: A dictionary containing the status and settings for this side.
    """
    return {
      'status': data['status'][self.type],
      'settings': data['settings'][self.type],
      'vitals': data['vitals'][self.type],
    }

  async def set_active(self, active: bool) -> None:
    """
    Set the active state for this side of the Free Sleep Pod device.

    :param active: The desired active state (True for on, False for off).
    """
    json_data = {self.type: {'isOn': active}}
    await self.pod.api.update_device_status(json_data)

    data = self.coordinator.data
    data['status'][self.type]['isOn'] = active
    self.coordinator.async_set_updated_data(data)

  async def set_target_temperature(self, temperature_f: float) -> None:
    """
    Set the target temperature for this side of the Free Sleep Pod device.

    :param temperature_f: The desired target temperature in Fahrenheit.
    """
    json_data = {self.type: {'targetTemperatureF': temperature_f}}
    await self.pod.api.update_device_status(json_data)

    data = self.coordinator.data
    data['settings'][self.type]['targetTemperatureF'] = temperature_f
    self.coordinator.async_set_updated_data(data)

  async def set_away_mode(self, enabled: bool) -> None:
    """
    Enable or disable away mode for this side of the Free Sleep Pod device.

    :param enabled: True to enable away mode, False to disable.
    """
    json_data = {self.type: {'awayMode': enabled}}
    await self.pod.api.update_settings(json_data)

    data = self.coordinator.data
    data['settings'][self.type]['awayMode'] = enabled
    self.coordinator.async_set_updated_data(data)
