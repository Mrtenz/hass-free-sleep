"""Home Assistant integration for Free Sleep Pod devices."""

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FreeSleepAPI
from .constants import DOMAIN
from .logger import log
from .pod import Pod

PLATFORMS = [
  Platform.BINARY_SENSOR,
  Platform.BUTTON,
  Platform.CLIMATE,
  Platform.NUMBER,
  Platform.SENSOR,
  Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  """
  Set up Free Sleep Pod from a config entry.

  This assumes the config entry has a "host" field in its data.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :return: True if setup was successful.
  """
  api = FreeSleepAPI(entry.data['host'], async_get_clientsession(hass))
  status = await api.fetch_device_status()

  pod = Pod(hass, entry, status['hubVersion'], entry.data['host'])
  coordinator = DataUpdateCoordinator(
    hass,
    log,
    name=pod.name,
    update_method=pod.async_fetch_state,
    update_interval=timedelta(seconds=30),
  )

  await coordinator.async_config_entry_first_refresh()

  hass.data.setdefault(DOMAIN, {})
  hass.data[DOMAIN][entry.entry_id] = (
    pod,
    coordinator,
  )

  await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
  return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  """
  Unload a config entry.

  :param hass: The Home Assistant instance.
  :param entry: The configuration entry.
  :return: True if unload was successful.
  """
  unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
  if unload_ok:
    hass.data[DOMAIN].pop(entry.entry_id)

  return unload_ok
