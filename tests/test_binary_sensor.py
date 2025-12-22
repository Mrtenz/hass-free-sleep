"""Tests for the binary sensor platform."""

from copy import deepcopy

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry
from syrupy import SnapshotAssertion

from custom_components.free_sleep.constants import (
  DOMAIN,
)


async def test_binary_sensor_platform(
  hass: HomeAssistant,
  integration: MockConfigEntry,
  snapshot: SnapshotAssertion,
) -> None:
  """Test the binary sensor platform setup."""
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
      and entry.domain == 'binary_sensor'
    ],
    key=lambda entry: entry['entity_id'],
  )

  assert entries == snapshot


async def test_binary_sensor_priming(
  hass: HomeAssistant,
  integration: MockConfigEntry,
) -> None:
  """Test `binary_sensor.pod_4_priming`."""
  binary_sensor = hass.states.get('binary_sensor.pod_4_priming')

  assert isinstance(binary_sensor, State)
  assert binary_sensor.state == 'off'
  assert binary_sensor.attributes.get('friendly_name') == 'Pod 4 Priming'
  assert binary_sensor.attributes.get('icon') == 'mdi:water-pump-off'

  _pod, coordinator = hass.data[DOMAIN][integration.entry_id]
  new_data = deepcopy(coordinator.data)
  new_data['status']['isPriming'] = True

  coordinator.async_set_updated_data(new_data)
  await hass.async_block_till_done()

  binary_sensor = hass.states.get('binary_sensor.pod_4_priming')
  assert isinstance(binary_sensor, State)
  assert binary_sensor.state == 'on'
  assert binary_sensor.attributes.get('icon') == 'mdi:water-pump'


async def test_binary_sensor_water_level(
  hass: HomeAssistant,
  integration: MockConfigEntry,
) -> None:
  """Test `binary_sensor.pod_4_water_level`."""
  binary_sensor = hass.states.get('binary_sensor.pod_4_water_level')

  assert isinstance(binary_sensor, State)
  assert binary_sensor.state == 'off'
  assert binary_sensor.attributes.get('friendly_name') == 'Pod 4 Water Level'
  assert binary_sensor.attributes.get('icon') == 'mdi:water-check'

  _pod, coordinator = hass.data[DOMAIN][integration.entry_id]
  new_data = deepcopy(coordinator.data)
  new_data['status']['waterLevel'] = False

  coordinator.async_set_updated_data(new_data)
  await hass.async_block_till_done()

  binary_sensor = hass.states.get('binary_sensor.pod_4_water_level')
  assert isinstance(binary_sensor, State)
  assert binary_sensor.state == 'on'
  assert binary_sensor.attributes.get('icon') == 'mdi:water-remove'


async def test_binary_sensor_side_presence(
  hass: HomeAssistant,
  integration: MockConfigEntry,
) -> None:
  """
  Test `binary_sensor.pod_4_left_presence` and
  `binary_sensor.pod_4_right_presence`.
  """
  left_sensor = hass.states.get('binary_sensor.pod_4_left_presence')
  right_sensor = hass.states.get('binary_sensor.pod_4_right_presence')

  assert isinstance(left_sensor, State)
  assert left_sensor.state == 'off'
  assert left_sensor.attributes.get('friendly_name') == 'Pod 4 Left Presence'
  assert left_sensor.attributes.get('icon') == 'mdi:bed-empty'

  assert isinstance(right_sensor, State)
  assert right_sensor.state == 'off'
  assert right_sensor.attributes.get('friendly_name') == 'Pod 4 Right Presence'
  assert right_sensor.attributes.get('icon') == 'mdi:bed-empty'

  _pod, coordinator = hass.data[DOMAIN][integration.entry_id]
  new_data = deepcopy(coordinator.data)
  new_data['presence']['left']['present'] = True
  new_data['presence']['right']['present'] = True

  coordinator.async_set_updated_data(new_data)
  await hass.async_block_till_done()

  left_sensor = hass.states.get('binary_sensor.pod_4_left_presence')
  right_sensor = hass.states.get('binary_sensor.pod_4_right_presence')

  assert isinstance(left_sensor, State)
  assert left_sensor.state == 'on'
  assert left_sensor.attributes.get('icon') == 'mdi:bed'

  assert isinstance(right_sensor, State)
  assert right_sensor.state == 'on'
  assert right_sensor.attributes.get('icon') == 'mdi:bed'
