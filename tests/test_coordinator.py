"""Tests for the coordinator module."""

import logging
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.free_sleep.api import FreeSleepAPI
from custom_components.free_sleep.constants import DOMAIN
from custom_components.free_sleep.coordinator import FreeSleepCoordinator
from tests.helpers import Url


async def test_is_vitals_valid_no_data(
  hass: HomeAssistant,
  api: FreeSleepAPI,
) -> None:
  """is_vitals_valid returns False when the coordinator has no data yet."""
  coordinator = FreeSleepCoordinator(hass, logging.getLogger(__name__), api)
  assert coordinator.is_vitals_valid('left') is False


async def test_is_vitals_valid_no_timer(
  hass: HomeAssistant,
  integration: MockConfigEntry,
) -> None:
  """is_vitals_valid returns False when presence is False with no timer set."""
  _pod, coordinator = hass.data[DOMAIN][integration.entry_id]

  coordinator.presence_false_since.clear()

  assert coordinator.is_vitals_valid('left') is False
  assert coordinator.is_vitals_valid('right') is False


async def test_presence_false_since_cleared_on_refresh(  # noqa: PLR0913
  hass: HomeAssistant,
  api: FreeSleepAPI,
  http: aioresponses,
  url: Url,
  mock_device_status: dict[str, Any],
  mock_settings: dict[str, Any],
  mock_services: dict[str, Any],
  mock_vitals: dict[str, Any],
) -> None:
  """presence_false_since is cleared when presence becomes True on refresh."""
  coordinator = FreeSleepCoordinator(hass, logging.getLogger(__name__), api)

  coordinator.presence_false_since = {
    'left': datetime.now(UTC) - timedelta(minutes=1),
    'right': datetime.now(UTC) - timedelta(minutes=1),
  }

  http.get(url('/api/deviceStatus'), payload=mock_device_status)
  http.get(url('/api/settings'), payload=mock_settings)
  http.get(url('/api/services'), payload=mock_services)
  http.get(
    re.compile(r'.*/api/metrics/vitals/summary\?.*side=left.*'),
    payload=mock_vitals,
  )
  http.get(
    re.compile(r'.*/api/metrics/vitals/summary\?.*side=right.*'),
    payload=mock_vitals,
  )
  http.get(
    url('/api/metrics/presence'),
    payload={
      'left': {'present': True, 'lastUpdatedAt': '2025-12-18T14:00:00-06:00'},
      'right': {'present': True, 'lastUpdatedAt': '2025-12-18T14:00:00-06:00'},
    },
  )

  await coordinator.async_refresh()

  assert 'left' not in coordinator.presence_false_since
  assert 'right' not in coordinator.presence_false_since
