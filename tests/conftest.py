"""
Test configuration and mock data fixtures for FreeSleepAPI.

This module provides pytest fixtures to create a FreeSleepAPI client and
mock responses for device status, settings, etc.
"""

import logging
from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from yarl import URL

from custom_components.free_sleep import DOMAIN, FreeSleepAPI
from custom_components.free_sleep.constants import SERVER_INFO_URL
from tests.helpers import AssertPost, Json, Url


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
  enable_custom_integrations: None,  # noqa: ARG001
) -> None:
  """Enable custom integrations for all tests."""
  return


@pytest.fixture(autouse=True)
def auto_configure_logging(caplog: pytest.LogCaptureFixture) -> None:
  """
  Configure logging for the tests to only show errors by default.

  Behaviour can be overridden in individual tests using the `caplog` fixture.
  """
  caplog.set_level(logging.ERROR)


@pytest.fixture
def http() -> Generator[aioresponses, Any]:
  """Fixture to mock `aiohttp` requests."""
  with aioresponses() as mock:
    yield mock


@pytest.fixture
def assert_post(http: aioresponses) -> AssertPost:
  """
  Assert that a POST request was made to the given URL and with expected JSON
  data.
  """

  def _assert(url: str, json: Json = None, requests: int = 1) -> None:
    calls = http.requests.get(('POST', URL(url)), [])
    assert len(calls) == requests

    (_args, kwargs) = calls[0]
    assert kwargs.get('json') == json

  return _assert


@pytest.fixture
def url() -> Url:
  """Fixture to generate full URLs for the API."""

  def _url(path: str | None = '') -> str:
    return f'http://example.com{path}'

  return _url


@pytest.fixture
async def api(url: Callable[[str], str]) -> AsyncGenerator[FreeSleepAPI, Any]:
  """Fixture to create a FreeSleepAPI client."""
  async with ClientSession() as session:
    yield FreeSleepAPI(host=url(), session=session)


@pytest.fixture
def mock_device_status() -> dict[str, Any]:
  """Fixture to provide a mock device status response."""
  return {
    'left': {
      'currentTemperatureLevel': -26,
      'currentTemperatureF': 75,
      'targetTemperatureF': 75,
      'secondsRemaining': 39656,
      'isOn': True,
      'isAlarmVibrating': False,
    },
    'right': {
      'currentTemperatureLevel': -64,
      'currentTemperatureF': 65,
      'targetTemperatureF': 77,
      'secondsRemaining': 0,
      'isOn': False,
      'isAlarmVibrating': False,
    },
    'coverVersion': 'Pod 4',
    'hubVersion': 'Pod 4',
    'freeSleep': {'version': '2.1.3', 'branch': 'main'},
    'waterLevel': 'true',
    'isPriming': False,
    'settings': {'v': 1, 'gainLeft': 400, 'gainRight': 400, 'ledBrightness': 0},
    'wifiStrength': 82,
  }


@pytest.fixture
def mock_settings() -> dict[str, Any]:
  """Fixture to provide a mock settings response."""
  return {
    'id': 'c2471234-2a72-4f6d-89d1-f7a617d1084d',
    'timeZone': 'Europe/Berlin',
    'temperatureFormat': 'celsius',
    'rebootDaily': True,
    'left': {
      'name': 'Left',
      'awayMode': False,
      'scheduleOverrides': {
        'temperatureSchedules': {'disabled': False, 'expiresAt': ''},
        'alarm': {'disabled': False, 'timeOverride': '', 'expiresAt': ''},
      },
      'taps': {
        'doubleTap': {
          'type': 'temperature',
          'change': 'decrement',
          'amount': 1,
        },
        'tripleTap': {
          'type': 'temperature',
          'change': 'increment',
          'amount': 1,
        },
        'quadTap': {
          'type': 'alarm',
          'behavior': 'dismiss',
          'snoozeDuration': 60,
          'inactiveAlarmBehavior': 'power',
        },
      },
    },
    'right': {
      'name': 'Right',
      'awayMode': False,
      'scheduleOverrides': {
        'temperatureSchedules': {'disabled': False, 'expiresAt': ''},
        'alarm': {'disabled': False, 'timeOverride': '', 'expiresAt': ''},
      },
      'taps': {
        'doubleTap': {
          'type': 'temperature',
          'change': 'decrement',
          'amount': 1,
        },
        'tripleTap': {
          'type': 'temperature',
          'change': 'increment',
          'amount': 1,
        },
        'quadTap': {
          'type': 'alarm',
          'behavior': 'dismiss',
          'snoozeDuration': 60,
          'inactiveAlarmBehavior': 'power',
        },
      },
    },
    'primePodDaily': {'enabled': True, 'time': '14:00'},
  }


@pytest.fixture
def mock_services() -> dict[str, Any]:
  """Fixture to provide a mock services response."""
  return {
    'sentryLogging': {'enabled': True},
    'biometrics': {
      'enabled': True,
      'jobs': {
        'installation': {
          'name': 'Biometrics installation',
          'message': '',
          'status': 'healthy',
          'description': 'Whether or not biometrics was installed successfully',
          'timestamp': '',
        },
        'stream': {
          'name': 'Biometrics stream',
          'message': '',
          'status': 'healthy',
          'description': 'Consumes the sensor data as a stream and calculates'
          'biometrics',
          'timestamp': '2025-12-04T11:06:15.795394+00:00',
        },
        'analyzeSleepLeft': {
          'name': 'Analyze sleep - left',
          'message': '',
          'status': 'healthy',
          'description': 'Analyzes sleep period',
          'timestamp': '2025-12-04T08:01:43.529467+00:00',
        },
        'analyzeSleepRight': {
          'name': 'Analyze sleep - right',
          'message': 'healthy',
          'status': 'failed',
          'description': 'Analyzes sleep period',
          'timestamp': '2025-11-25T10:18:45.446482+00:00',
        },
        'calibrateLeft': {
          'name': 'Calibration job - Left',
          'message': '',
          'status': 'healthy',
          'description': 'Calculates presence thresholds for cap sensor data',
          'timestamp': '2025-12-03T13:00:46.590535+00:00',
        },
        'calibrateRight': {
          'name': 'Calibration job - Right',
          'message': '',
          'status': 'healthy',
          'description': 'Calculates presence thresholds for cap sensor data',
          'timestamp': '2025-12-03T13:30:55.128390+00:00',
        },
      },
    },
  }


@pytest.fixture
def mock_vitals() -> dict[str, Any]:
  """Fixture to provide a mock vitals response."""
  return {
    'heartRate': 60,
    'respirationRate': 15,
    'avgHeartRate': 50,
    'avgHRV': 40,
    'avgBreathingRate': 14,
  }


@pytest.fixture
def mock_presence() -> dict[str, Any]:
  """Fixture to provide a mock presence response."""
  return {
    'left': {
      'present': False,
      'lastUpdatedAt': '2025-12-18T13:59:59-06:00',
    },
    'right': {
      'present': False,
      'lastUpdatedAt': '2025-12-18T13:59:59-06:00',
    },
  }


@pytest.fixture
def mock_latest_version() -> dict[str, Any]:
  """Fixture to provide a mock latest firmware version response."""
  return {'version': '2.2.0', 'branch': 'main'}


@pytest.fixture
def mock_coordinator_data(
  mock_device_status: dict[str, Any],
  mock_settings: dict[str, Any],
  mock_services: dict[str, Any],
  mock_vitals: dict[str, Any],
  mock_presence: dict[str, Any],
) -> dict[str, Any]:
  """Fixture to provide mock coordinator data."""
  return {
    'services': mock_services,
    'settings': mock_settings,
    'status': mock_device_status,
    'vitals': {
      'left': mock_vitals,
      'right': mock_vitals,
    },
    'presence': {
      'left': mock_presence['left'],
      'right': mock_presence['right'],
    },
  }


@pytest.fixture
def mock_config_entry(
  url: Callable[[str], str],
) -> MockConfigEntry:
  """Fixture to provide a mock config entry."""
  return MockConfigEntry(
    domain=DOMAIN,
    data={
      'host': url(),
    },
    entry_id='test',
    version=0,
    minor_version=1,
  )


@pytest.fixture
async def integration(  # noqa: PLR0913
  hass: HomeAssistant,
  http: aioresponses,
  url: Callable[[str], str],
  mock_device_status: dict[str, Any],
  mock_settings: dict[str, Any],
  mock_services: dict[str, Any],
  mock_vitals: dict[str, Any],
  mock_presence: dict[str, Any],
  mock_latest_version: dict[str, Any],
  mock_config_entry: MockConfigEntry,
) -> MockConfigEntry:
  """
  Fixture to set up the FreeSleep integration.

  It mocks the necessary HTTP responses and sets up the config entry in Home
  Assistant.
  """
  http.get(url('/api/deviceStatus'), payload=mock_device_status, repeat=True)
  http.get(url('/api/settings'), payload=mock_settings, repeat=True)
  http.get(url('/api/services'), payload=mock_services, repeat=True)
  http.get(
    url('/api/metrics/vitals/summary?side=left'),
    payload=mock_vitals,
    repeat=True,
  )
  http.get(
    url('/api/metrics/vitals/summary?side=right'),
    payload=mock_vitals,
    repeat=True,
  )
  http.get(url('/api/metrics/presence'), payload=mock_presence, repeat=True)
  http.get(SERVER_INFO_URL, payload=mock_latest_version, repeat=True)

  mock_config_entry.add_to_hass(hass)

  await hass.config_entries.async_setup(mock_config_entry.entry_id)
  await hass.async_block_till_done()
  return mock_config_entry
