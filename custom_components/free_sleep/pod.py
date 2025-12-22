"""Classes to represent a Free Sleep Pod device and its sides."""

from typing import Any, TypedDict, Unpack

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FreeSleepAPI
from .constants import PodSide
from .coordinator import PodState
from .logger import log


class Pod:
  """A class that represents a Free Sleep Pod device."""

  manufacturer: str = 'Eight Sleep'

  host: str

  def __init__(
    self,
    hass: HomeAssistant,
    coordinator: DataUpdateCoordinator[PodState],
    entry: ConfigEntry,
    host: str,
  ) -> None:
    """
    Initialize the Free Sleep Pod device.

    :param hass: The Home Assistant instance.
    :param coordinator: The data update coordinator for the pod.
    :param entry: The configuration entry.
    :param host: The host address of the Free Sleep Pod device.
    """
    self.hass = hass
    self.coordinator = coordinator
    self.api = FreeSleepAPI(host, async_get_clientsession(hass))

    name = coordinator.data['status']['hubVersion']

    self.id = entry.entry_id
    self.model = name
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

  async def execute_command(self, command: str, value: str) -> dict[str, Any]:
    """
    Execute a command on the Free Sleep Pod device.

    :param command: The command to execute.
    :param value: The value associated with the command.
    """
    json_data = {'command': command, 'arg': value}
    return await self.api.execute(json_data)

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

  async def set_prime_daily_time(self, time: str) -> None:
    """
    Set the daily priming time for the Free Sleep Pod device.

    :param time: The desired priming time in HH:MM format.
    """
    json_data = {'primePodDaily': {'time': time}}
    await self.api.update_settings(json_data)

    data = self.coordinator.data
    data['settings']['primePodDaily']['time'] = time
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

  async def set_biometrics(self, enabled: bool) -> None:
    """
    Enable or disable biometrics for the Free Sleep Pod device.

    :param enabled: True to enable biometrics, False to disable.
    """
    json_data = {'biometrics': {'enabled': enabled}}
    await self.api.update_services(json_data)

    data = self.coordinator.data
    data['services']['biometrics']['enabled'] = enabled
    self.coordinator.async_set_updated_data(data)

  async def prime(self) -> None:
    """Prime the Free Sleep Pod device."""
    json_data = {'isPriming': True}
    await self.api.update_device_status(json_data)

    data = self.coordinator.data
    data['status']['isPriming'] = True
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
    self.name = f'{pod.model} {coordinator.data["settings"][side]["name"]}'

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
      'via_device': (self.pod.manufacturer, self.pod.id),
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
      'presence': data['presence'][self.type],
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

  class ScheduleOptions(TypedDict):
    """
    Typed dict representing the schedule options for a Free Sleep Pod side,
    consisting of days of the week and the schedule dictionary.
    """

    days_of_week: list[str]
    schedule: dict

  async def set_schedule(self, **kwargs: Unpack[ScheduleOptions]) -> None:
    """
    Set the sleep schedule for this side of the Free Sleep Pod device.

    :param kwargs: Keyword arguments passed to set_schedule.
    """
    days_of_week = kwargs.get('days_of_week')
    schedule = kwargs.get('schedule')

    json_data = {self.type: dict.fromkeys(days_of_week, schedule)}

    log.debug(
      f'Setting schedule for side "{self.type}" with data "{json_data}".'
    )
    await self.pod.api.update_schedule(json_data)
