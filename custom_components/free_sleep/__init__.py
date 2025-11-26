"""Home Assistant integration for Free Sleep Pod devices."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import FreeSleepAPI
from .constants import DOMAIN
from .coordinator import FreeSleepCoordinator
from .logger import log
from .pod import Pod
from .services import register_services

PLATFORMS: list[Platform] = [
  Platform.BINARY_SENSOR,
  Platform.BUTTON,
  Platform.CLIMATE,
  Platform.NUMBER,
  Platform.SENSOR,
  Platform.SWITCH,
  Platform.TIME,
  Platform.UPDATE,
]


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
  """Set up the Free Sleep integration."""
  await register_services(hass)

  return True


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
  name = status['hubVersion']

  coordinator = FreeSleepCoordinator(
    hass,
    log,
    api,
    name,
  )

  pod = Pod(hass, coordinator, entry, status['hubVersion'], entry.data['host'])

  hass.data.setdefault(DOMAIN, {})
  hass.data[DOMAIN][entry.entry_id] = (
    pod,
    coordinator,
  )

  await coordinator.async_config_entry_first_refresh()
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
