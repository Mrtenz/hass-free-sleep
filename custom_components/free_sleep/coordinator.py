"""
A module that defines the data update coordinator for Free Sleep Pod devices,
which is responsible for fetching and updating the device state periodically.
"""

from asyncio import gather
from datetime import timedelta
from logging import Logger
from typing import Any, TypedDict

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator,
  UpdateFailed,
)

from .api import FreeSleepAPI
from .constants import PodSide
from .logger import log


class PodState(TypedDict):
  """A class that represents the state of a Free Sleep Pod device."""

  services: dict[str, Any]
  settings: dict[str, Any]
  status: dict[str, Any]
  vitals: dict[PodSide, Any]
  presence: dict[PodSide, Any]


class FirmwareState(TypedDict):
  """A class that represents the firmware state of a Free Sleep Pod device."""

  current_version: str | None
  latest_version: str | None


class FreeSleepCoordinator(DataUpdateCoordinator[PodState]):
  """A class that coordinates data updates for a Free Sleep Pod device."""

  def __init__(
    self,
    hass: HomeAssistant,
    log: Logger,
    api: FreeSleepAPI,
    update_interval: int = 30,
    config_entry: ConfigEntry | None = None,
  ) -> None:
    """
    Initialize the Free Sleep Coordinator.

    :param hass: The Home Assistant instance.
    :param api: The Free Sleep API instance.
    """
    super().__init__(
      hass,
      log,
      name='Free Sleep Coordinator',
      update_method=self._async_update_data,
      update_interval=timedelta(seconds=update_interval),
      config_entry=config_entry,
    )

    self.api = api

  async def _async_update_data(self) -> PodState:
    """
    Fetch the latest data from the Free Sleep Pod device.

    :return: A `PodState` dictionary containing the latest status, settings, and
    vitals.
    """
    requests = [
      self.api.fetch_device_status(),
      self.api.fetch_settings(),
      self.api.fetch_vitals('left'),
      self.api.fetch_vitals('right'),
      self.api.fetch_services(),
      self.api.fetch_presence(),
    ]

    try:
      (
        status,
        settings,
        vitals_left,
        vitals_right,
        services,
        presence,
      ) = await gather(*requests)
    except TimeoutError as error:
      log.error(
        f'Timeout while fetching data from device at "{self.api.host}".'
      )
      raise UpdateFailed from error
    except ClientError as error:
      log.error(
        f'Client error while fetching data from device at "{self.api.host}": '
        f'{error}'
      )
      raise UpdateFailed from error
    except Exception as error:
      log.error(
        'Unexpected error while fetching data from device at'
        f'"{self.api.host}": {error}'
      )
      raise UpdateFailed from error

    vitals_dict: dict[PodSide, Any] = {
      'left': vitals_left,
      'right': vitals_right,
    }

    presence_dict: dict[PodSide, Any] = {
      'left': presence.get('left', {}),
      'right': presence.get('right', {}),
    }

    return PodState(
      services=services,
      settings=settings,
      status=status,
      vitals=vitals_dict,
      presence=presence_dict,
    )


class FirmwareUpdateCoordinator(DataUpdateCoordinator[FirmwareState]):
  """
  A class that coordinates fetching the latest firmware version from GitHub.
  This is defined separately to avoid making frequent requests to GitHub when
  the main coordinator updates every 30 seconds.
  """

  def __init__(
    self, hass: HomeAssistant, log: Logger, api: FreeSleepAPI
  ) -> None:
    """
    Initialize the GitHub Update Coordinator.

    :param hass: The Home Assistant instance.
    :param log: Logger instance.
    :param api: The Free Sleep API instance.
    """
    super().__init__(
      hass,
      log,
      name='Firmware Update Coordinator',
      update_method=self._async_update_data,
      update_interval=timedelta(hours=1),
    )

    self.api = api

  async def _async_update_data(self) -> FirmwareState:
    """
    Fetch the latest firmware version from GitHub.

    :return: The latest firmware version as a string, or None if not available.
    """
    try:
      current_version, latest_version = await gather(
        self.api.fetch_current_version(), self.api.fetch_latest_version()
      )

      return FirmwareState(
        current_version=current_version, latest_version=latest_version
      )
    except Exception as error:
      log.error('Unexpected error while fetching firmware version.')
      raise UpdateFailed from error
