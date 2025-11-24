"""
Client for interacting with Free Sleep devices over the HTTP API.

This module provides the `FreeSleepAPI` class, which allows fetching device
status and settings, as well as updating device configurations.
"""

from collections.abc import Mapping
from typing import Any

from aiohttp import ClientResponse, ClientSession

from .constants import (
  DEVICE_STATUS_ENDPOINT,
  SETTINGS_ENDPOINT,
  VITALS_SUMMARY_ENDPOINT,
  PodSide,
)
from .logger import log


class FreeSleepAPI:
  """An API client to interact with Free Sleep devices."""

  host: str
  session: ClientSession

  def __init__(self, host: str, session: ClientSession) -> None:
    """
    Initialize the Free Sleep API client.

    :param host: The host URL of the Free Sleep device.
    :param session: The `aiohttp` ClientSession to use for HTTP requests.
    """
    log.debug(f'Initializing Free Sleep API with host "{host}".')

    self.host = host
    self.session = session

  async def parse_response(self, response: ClientResponse) -> dict[str, Any]:
    """
    Parse the JSON response from the Free Sleep device.

    This handles the case where the response status is 204 (No Content), and
    returns an empty dictionary in that case.

    :param response: The HTTP response object.
    :return: A dictionary containing the parsed JSON data.
    """
    if response.status == 204:
      log.debug('-> No content')
      return {}

    data = await response.json()
    log.debug(f'-> {data}')
    return data

  async def get(
    self, url: str, params: Mapping[str, str] | None = None
  ) -> dict[str, Any]:
    """
    Send a GET request to the specified URL and return the JSON response.

    :param url: The URL to send the GET request to.
    :param params: Optional query parameters to include in the GET request.
    :return: A dictionary containing the JSON response.
    """
    log.debug(f'GET {url}')

    async with self.session.get(url, params=params, timeout=10) as response:
      response.raise_for_status()
      return await self.parse_response(response)

  async def post(self, url: str, json_data: dict[str, Any]) -> dict[str, Any]:
    """
    Send a POST request to the specified URL with JSON data and return the JSON
    response.

    :param url: The URL to send the POST request to.
    :param json_data: The JSON data to include in the POST request.
    :return: A dictionary containing the JSON response, if any.
    """
    log.debug(f'POST {url} with data {json_data}')

    async with self.session.post(url, json=json_data, timeout=10) as response:
      response.raise_for_status()
      return await self.parse_response(response)

  async def fetch_device_status(self) -> dict[str, Any]:
    """
    Fetch the current status from the Free Sleep device.

    :return: A dictionary containing the device status.
    """
    url = f'{self.host}{DEVICE_STATUS_ENDPOINT}'
    log.debug(f'Fetching device status from device at "{url}".')

    return await self.get(url)

  async def fetch_settings(self) -> dict[str, Any]:
    """
    Fetch the current settings from the Free Sleep device.

    :return: A dictionary containing the device settings.
    """
    url = f'{self.host}{SETTINGS_ENDPOINT}'
    log.debug(f'Fetching settings from device at "{url}".')

    return await self.get(url)

  async def fetch_vitals(self, side: PodSide) -> dict[str, Any]:
    """
    Fetch the current vitals for a specific side of the Free Sleep device.

    :param side: The side of the pod ("left" or "right").
    :return: A dictionary containing the side vitals.
    """
    url = f'{self.host}{VITALS_SUMMARY_ENDPOINT}'
    log.debug(f'Fetching vitals for side "{side}" from device at "{url}".')

    return await self.get(url, params={'side': side})

  async def set_side_active(self, side: PodSide, active: bool) -> None:
    """
    Set the active state for a specific side of the Free Sleep device.

    :param side: The side of the pod ("left" or "right").
    :param active: The desired active state (True for on, False for off).
    """
    url = f'{self.host}{DEVICE_STATUS_ENDPOINT}'
    log.debug(
      f'Setting side "{side}" active state to {active} on device at "{url}".'
    )

    json_data = {side: {'isOn': active}}

    await self.post(url, json_data)

  async def set_side_target_temperature(
    self, side: PodSide, temperature_f: float
  ) -> None:
    """
    Set the target temperature for a specific side of the Free Sleep device.

    :param side: The side of the pod ("left" or "right").
    :param temperature_f: The desired target temperature in Fahrenheit.
    """
    url = f'{self.host}{DEVICE_STATUS_ENDPOINT}'
    log.debug(
      f'Setting side "{side}" target temperature to {temperature_f}°F on '
      f'device at "{url}".'
    )

    json_data = {side: {'targetTemperatureF': temperature_f}}

    await self.post(url, json_data)

  async def set_prime_daily(self, enabled: bool) -> None:
    """
    Enable or disable daily priming for the Free Sleep Pod device.

    :param enabled: Whether to enable (True) or disable (False) daily priming.
    """
    url = f'{self.host}{SETTINGS_ENDPOINT}'
    log.debug(f'Setting daily priming to {enabled} on device at "{url}".')

    json_data = {'primePodDaily': {'enabled': enabled}}

    await self.post(url, json_data)

  async def set_reboot_daily(self, enabled: bool) -> None:
    """
    Enable or disable daily rebooting for the Free Sleep Pod device.

    :param enabled: Whether to enable (True) or disable (False) daily rebooting.
    """
    url = f'{self.host}{SETTINGS_ENDPOINT}'
    log.debug(f'Setting daily rebooting to {enabled} on device at "{url}".')

    json_data = {'rebootDaily': enabled}

    await self.post(url, json_data)

  async def set_led_brightness(self, brightness: int) -> None:
    """
    Set the LED brightness on the Free Sleep device.

    :param brightness: The desired brightness level (0-100).
    """
    url = f'{self.host}{DEVICE_STATUS_ENDPOINT}'
    log.debug(f'Setting LED brightness to {brightness}% on device at "{url}".')

    json_data = {'settings': {'ledBrightness': brightness}}

    await self.post(url, json_data)
