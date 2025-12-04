"""
Test configuration and mock data fixtures for FreeSleepAPI.

This module provides pytest fixtures to create a FreeSleepAPI client and
mock responses for device status, settings, etc.
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from aiohttp import ClientSession
from pytest_httpserver import HTTPServer

from custom_components.free_sleep import FreeSleepAPI


@pytest.fixture
async def api(httpserver: HTTPServer) -> AsyncGenerator[FreeSleepAPI, Any]:
  """Fixture to create a FreeSleepAPI client."""
  async with ClientSession() as session:
    yield FreeSleepAPI(host=httpserver.url_for('/'), session=session)


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
  return {'heartRate': 60, 'respirationRate': 15}


@pytest.fixture
def mock_latest_version() -> dict[str, Any]:
  """Fixture to provide a mock latest firmware version response."""
  return {'version': '2.2.0', 'branch': 'main'}
