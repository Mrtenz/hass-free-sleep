"""Tests for the Free Sleep integration's `__init__.py` module."""

from typing import Any
from unittest.mock import patch

from habluetooth.manager import Callable
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry
from syrupy.data import Snapshot

from custom_components.free_sleep import DOMAIN, async_setup, async_setup_entry


async def test_async_setup_register_services(
  hass: HomeAssistant, snapshot: Snapshot
) -> None:
  """Test the `async_setup` function, registering services to Home Assistant."""
  assert await async_setup(hass, {})

  services = hass.services.async_services()
  domain_services = services.get(DOMAIN)
  assert domain_services

  service_data = {
    service_name: {
      'name': service.job.name,
      'schema': str(service.schema),
      'supports_response': service.supports_response,
      'type': service.job.job_type,
    }
    for service_name, service in domain_services.items()
  }

  assert service_data == snapshot


async def test_async_setup_entry(
  hass: HomeAssistant,
  url: Callable[[str], str],
  mock_coordinator_data: dict[str, Any],
) -> None:
  """Test the `async_setup_entry` function for setting up a config entry."""
  entry = MockConfigEntry(
    domain=DOMAIN,
    data={
      'host': url(),
    },
    entry_id='test-entry-id',
  )

  def refresh(coordinator: DataUpdateCoordinator) -> None:
    coordinator.data = mock_coordinator_data

  with (
    patch(
      'custom_components.free_sleep.FreeSleepCoordinator.async_config_entry_first_refresh',
      autospec=True,
      side_effect=refresh,
    ),
    patch(
      'homeassistant.config_entries.ConfigEntries.async_forward_entry_setups'
    ),
  ):
    assert await async_setup_entry(hass, entry)
    await hass.async_block_till_done()

  assert hass.data[DOMAIN]
  assert hass.data[DOMAIN][entry.entry_id]
