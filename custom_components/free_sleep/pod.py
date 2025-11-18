"""Classes to represent a Free Sleep Pod device and its sides."""

from asyncio import gather
from typing import Any, TypedDict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FreeSleepAPI
from .constants import PodSide


class PodState(TypedDict):
  """A class that represents the state of a Free Sleep Pod device."""

  status: dict[str, Any]
  settings: dict[str, Any]
  vitals: dict[PodSide, Any]


class Pod:
  """A class that represents a Free Sleep Pod device."""

  manufacturer: str = 'Eight Sleep'

  host: str

  def __init__(
    self, hass: HomeAssistant, entry: ConfigEntry, name: str, host: str
  ) -> None:
    """
    Initialize the Free Sleep Pod device.

    :param hass: The Home Assistant instance.
    :param entry: The configuration entry.
    :param name: The name of the Free Sleep Pod device. This should be fetched
    from the device during setup.
    :param host: The host address of the Free Sleep Pod device.
    """
    self.hass = hass
    self.api = FreeSleepAPI(host, async_get_clientsession(hass))

    self.id = entry.entry_id
    self.model: str = name
    self.host = host
    self.name = name
    self.sides = [Side(hass, self, 'left'), Side(hass, self, 'right')]

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

  async def async_fetch_state(self) -> PodState:
    """
    Fetch the current state from the Free Sleep Pod device.

    :return: A dictionary containing the device status and settings.
    """
    requests = [
      self.api.fetch_device_status(),
      self.api.fetch_settings(),
      self.api.fetch_vitals('left'),
      self.api.fetch_vitals('right'),
    ]

    status, settings, vitals_left, vitals_right = await gather(*requests)
    return {
      'status': status,
      'settings': settings,
      'vitals': {
        'left': vitals_left,
        'right': vitals_right,
      },
    }

  async def set_prime_daily(self, enabled: bool) -> None:
    """
    Enable or disable daily priming for the Free Sleep Pod device.

    :param enabled: True to enable daily priming, False to disable.
    """
    await self.api.set_prime_daily(enabled)

  async def set_led_brightness(self, brightness: int) -> None:
    """
    Set the LED brightness for the Free Sleep Pod device.

    :param brightness: The desired brightness level (0-100).
    """
    await self.api.set_led_brightness(brightness)


class Side:
  """A class that represents a side of a Free Sleep Pod device."""

  def __init__(self, hass: HomeAssistant, pod: Pod, side: PodSide) -> None:
    """
    Initialize the Free Sleep Pod side.

    :param hass: The Home Assistant instance.
    :param pod: The Free Sleep Pod instance.
    :param side: The side of the pod ('left' or 'right').
    """
    self.hass = hass
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
    return await self.pod.api.set_side_active(self.type, active)

  async def set_target_temperature(self, temperature_f: float) -> None:
    """
    Set the target temperature for this side of the Free Sleep Pod device.

    :param temperature_f: The desired target temperature in Fahrenheit.
    """
    return await self.pod.api.set_side_target_temperature(
      self.type, temperature_f
    )
