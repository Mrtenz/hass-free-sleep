"""
A module that defines the data update coordinator for Free Sleep Pod devices,
which is responsible for fetching and updating the device state periodically.
"""

from asyncio import gather
from datetime import timedelta
from logging import Logger
from typing import Any, TypedDict

from aiohttp import ClientError
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

  status: dict[str, Any]
  settings: dict[str, Any]
  vitals: dict[PodSide, Any]


class FreeSleepCoordinator(DataUpdateCoordinator[PodState]):
  """A class that coordinates data updates for a Free Sleep Pod device."""

  def __init__(
    self, hass: HomeAssistant, log: Logger, api: FreeSleepAPI, name: str
  ) -> None:
    """
    Initialize the Free Sleep Coordinator.

    :param hass: The Home Assistant instance.
    :param api: The Free Sleep API instance.
    """
    super().__init__(
      hass,
      log,
      name=name,
      update_method=self._async_update_data,
      update_interval=timedelta(seconds=30),
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
    ]

    try:
      status, settings, vitals_left, vitals_right = await gather(*requests)
    except TimeoutError as error:
      log.error(
        f'Timeout while fetching data from device at "{self.api.host}".'
      )
      raise UpdateFailed from error
    except ClientError as error:
      log.error(
        f'Client error while fetching data from device at "{self.api.host}":'
        f'{error}'
      )
      raise UpdateFailed from error
    except Exception as error:
      log.error(
        'Unexpected error while fetching data from device at'
        f'"{self.api.host}": {error}'
      )
      raise UpdateFailed from error

    return PodState(
      status=status,
      settings=settings,
      vitals={'left': vitals_left, 'right': vitals_right},
    )
