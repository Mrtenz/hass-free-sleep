"""Tests for the sensor platform."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry
from syrupy import SnapshotAssertion

from custom_components.free_sleep.constants import DOMAIN


async def test_sensor_platform(
  hass: HomeAssistant,
  integration: MockConfigEntry,
  snapshot: SnapshotAssertion,
) -> None:
  """Test the sensor platform setup."""
  registry = entity_registry.async_get(hass)

  # Map registry entries to a simplified dict for the snapshot
  entries = sorted(
    [
      {
        'entity_id': entry.entity_id,
        'unique_id': entry.unique_id,
        'translation_key': entry.translation_key,
        'device_class': entry.device_class,
        'original_name': entry.original_name,
      }
      for entry in registry.entities.values()
      if entry.config_entry_id == integration.entry_id
      and entry.domain == 'sensor'
    ],
    key=lambda entry: entry['entity_id'],
  )

  assert entries == snapshot


VITALS_ENTITY_IDS = [
  'sensor.pod_4_left_heart_rate',
  'sensor.pod_4_left_respiration_rate',
  'sensor.pod_4_left_hrv',
  'sensor.pod_4_right_heart_rate',
  'sensor.pod_4_right_respiration_rate',
  'sensor.pod_4_right_hrv',
]

VITALS_EXPECTED_VALUES = [
  ('sensor.pod_4_left_heart_rate', '50'),
  ('sensor.pod_4_left_respiration_rate', '14'),
  ('sensor.pod_4_left_hrv', '40'),
  ('sensor.pod_4_right_heart_rate', '50'),
  ('sensor.pod_4_right_respiration_rate', '14'),
  ('sensor.pod_4_right_hrv', '40'),
]


@pytest.mark.usefixtures('integration')
async def test_vitals_sensors_available_during_grace_window(
  hass: HomeAssistant,
) -> None:
  """Vitals sensors still report values just after presence is lost."""
  # The integration fixture starts with present=False, so presence_false_since
  # is set to "now" — we are inside the 5-minute grace window.
  for entity_id, expected in VITALS_EXPECTED_VALUES:
    sensor = hass.states.get(entity_id)
    assert isinstance(sensor, State)
    assert sensor.state == expected, (
      f'{entity_id} should show {expected} within the grace window'
    )


async def test_vitals_sensors_unknown_after_grace_window(
  hass: HomeAssistant,
  integration: MockConfigEntry,
) -> None:
  """Vitals sensors report unknown once the grace window has elapsed."""
  _pod, coordinator = hass.data[DOMAIN][integration.entry_id]

  expired = datetime.now(UTC) - timedelta(minutes=6)
  coordinator.presence_false_since = {'left': expired, 'right': expired}

  coordinator.async_set_updated_data(coordinator.data)
  await hass.async_block_till_done()

  for entity_id in VITALS_ENTITY_IDS:
    sensor = hass.states.get(entity_id)
    assert isinstance(sensor, State)
    assert sensor.state == 'unknown', (
      f'{entity_id} should be unknown after the grace window'
    )


async def test_vitals_sensors_available_when_present(
  hass: HomeAssistant,
  integration: MockConfigEntry,
) -> None:
  """Vitals sensors report values when someone is present in bed."""
  _pod, coordinator = hass.data[DOMAIN][integration.entry_id]
  new_data = deepcopy(coordinator.data)
  new_data['presence']['left']['present'] = True
  new_data['presence']['right']['present'] = True

  coordinator.async_set_updated_data(new_data)
  await hass.async_block_till_done()

  for entity_id, expected in VITALS_EXPECTED_VALUES:
    sensor = hass.states.get(entity_id)
    assert isinstance(sensor, State)
    assert sensor.state == expected, (
      f'{entity_id} should be {expected} when present'
    )
