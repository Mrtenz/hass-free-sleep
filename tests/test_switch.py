"""Tests for the switch platform."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry
from syrupy import SnapshotAssertion


async def test_switch_platform(
  hass: HomeAssistant,
  integration: MockConfigEntry,
  snapshot: SnapshotAssertion,
) -> None:
  """Test the switch platform setup."""
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
      and entry.domain == 'switch'
    ],
    key=lambda entry: entry['entity_id'],
  )

  assert entries == snapshot
