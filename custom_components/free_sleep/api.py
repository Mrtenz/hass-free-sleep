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
  JOBS_ENDPOINT,
  SCHEDULES_ENDPOINT,
  SERVER_INFO_URL,
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

    data = await response.json(content_type=None)
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

  async def post(
    self, url: str, json_data: dict[str, Any] | list[Any]
  ) -> dict[str, Any]:
    """
    Send a POST request to the specified URL with JSON data and return the JSON
    response.

    :param url: The URL to send the POST request to.
    :param json_data: The JSON data to include in the POST request.
    :return: A dictionary containing the JSON response, if any.
    """
    log.debug(f'POST {url} with data "{json_data}".')

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

  async def fetch_current_version(self) -> str | None:
    """
    Fetch the current firmware version from the Free Sleep device.

    :return: The current firmware version as a string, or None if not available.
    """
    url = f'{self.host}{DEVICE_STATUS_ENDPOINT}'
    log.debug(f'Fetching current firmware version from device at "{url}".')

    data = await self.get(url)
    return data['freeSleep']['version']

  async def fetch_latest_version(self) -> str | None:
    """
    Fetch the latest firmware version available on GitHub.

    :return: The latest firmware version as a string, or None if not available.
    """
    log.debug(f'Fetching latest firmware version from "{SERVER_INFO_URL}".')

    data = await self.get(SERVER_INFO_URL)
    return data.get('version')

  async def update_device_status(self, json_data: dict[str, Any]) -> None:
    """
    Update the device status on the Free Sleep device.

    :param json_data: The JSON data to send in the update.
    """
    url = f'{self.host}{DEVICE_STATUS_ENDPOINT}'
    log.debug(
      f'Updating device status on device at "{url}" with data "{json_data}".'
    )

    await self.post(url, json_data)

  async def update_settings(self, json_data: dict[str, Any]) -> None:
    """
    Update the device settings on the Free Sleep device.

    :param json_data: The JSON data to send in the update.
    """
    url = f'{self.host}{SETTINGS_ENDPOINT}'
    log.debug(
      f'Updating settings on device at "{url}" with data "{json_data}".'
    )

    await self.post(url, json_data)

  async def update_schedule(self, json_data: dict[str, Any]) -> None:
    """
    Update the sleep schedule on the Free Sleep device.

    :param json_data: The JSON data representing the new schedule.
    """
    url = f'{self.host}{SCHEDULES_ENDPOINT}'
    log.debug(
      f'Updating schedule on device at "{url}" with data "{json_data}".'
    )

    await self.post(url, json_data)

  async def run_jobs(self, jobs: list[str]) -> None:
    """
    Run specified jobs on the Free Sleep device.

    :param jobs: A list of job names to run.
    """
    url = f'{self.host}{JOBS_ENDPOINT}'
    log.debug(f'Running jobs on device at "{url}" with data "{jobs}".')

    await self.post(url, jobs)
