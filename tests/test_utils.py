"""Tests for the `utils` module."""

import pytest
from homeassistant.const import UnitOfTemperature

from custom_components.free_sleep.utils import (
  schedule_to_fahrenheit,
  unit_to_fahrenheit,
)


@pytest.mark.parametrize(
  ('unit', 'value', 'expected'),
  [
    (UnitOfTemperature.CELSIUS, 0, 32),
    (UnitOfTemperature.CELSIUS, 100, 212),
    (UnitOfTemperature.CELSIUS, -40, -40),
    (UnitOfTemperature.KELVIN, 0, -460),
    (UnitOfTemperature.KELVIN, 373.15, 212),
    (UnitOfTemperature.KELVIN, 255.372, 0),
    (UnitOfTemperature.FAHRENHEIT, 32, 32),
    (UnitOfTemperature.FAHRENHEIT, 212, 212),
    (UnitOfTemperature.FAHRENHEIT, -40, -40),
  ],
)
def test_unit_to_fahrenheit(
  unit: UnitOfTemperature, value: float, expected: int
) -> None:
  """Test conversion of temperature values to Fahrenheit."""
  result = unit_to_fahrenheit(unit, value)
  assert result == expected


@pytest.mark.parametrize(
  ('unit', 'schedule', 'expected'),
  [
    (
      UnitOfTemperature.CELSIUS,
      {
        'alarm': {'alarmTemperature': 20},
        'power': {'onTemperature': 22},
        'temperatures': {'08:00': 18, '20:00': 21},
      },
      {
        'alarm': {'alarmTemperature': 68},
        'power': {'onTemperature': 72},
        'temperatures': {'08:00': 64, '20:00': 70},
      },
    ),
    (
      UnitOfTemperature.FAHRENHEIT,
      {
        'alarm': {'alarmTemperature': 68},
        'power': {'onTemperature': 72},
        'temperatures': {'08:00': 65, '20:00': 70},
      },
      {
        'alarm': {'alarmTemperature': 68},
        'power': {'onTemperature': 72},
        'temperatures': {'08:00': 65, '20:00': 70},
      },
    ),
    (
      UnitOfTemperature.KELVIN,
      {
        'alarm': {'alarmTemperature': 293.15},
        'power': {'onTemperature': 295.15},
        'temperatures': {'08:00': 291.15, '20:00': 294.15},
      },
      {
        'alarm': {'alarmTemperature': 68},
        'power': {'onTemperature': 72},
        'temperatures': {'08:00': 64, '20:00': 70},
      },
    ),
    (
      UnitOfTemperature.CELSIUS,
      {
        'alarm': {},
        'power': {},
        'temperatures': {},
      },
      {
        'alarm': {},
        'power': {},
        'temperatures': {},
      },
    ),
    (
      UnitOfTemperature.CELSIUS,
      {
        'alarm': {'alarmTemperature': 20},
      },
      {
        'alarm': {'alarmTemperature': 68},
      },
    ),
    (
      UnitOfTemperature.CELSIUS,
      {
        'power': {'onTemperature': 22},
      },
      {
        'power': {'onTemperature': 72},
      },
    ),
    (
      UnitOfTemperature.CELSIUS,
      {
        'temperatures': {'08:00': 18, '20:00': 21},
      },
      {
        'temperatures': {'08:00': 64, '20:00': 70},
      },
    ),
  ],
)
def test_schedule_to_fahrenheit(
  unit: UnitOfTemperature, schedule: dict, expected: dict
) -> None:
  """Test conversion of schedule temperature values to Fahrenheit."""
  result = schedule_to_fahrenheit(unit, schedule)
  assert result == expected
