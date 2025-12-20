"""Home Assistant integration for Free Sleep Pod devices."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_validation import (
  config_entry_only_config_schema,
)
from homeassistant.helpers.typing import ConfigType

from .api import FreeSleepAPI
from .constants import CONF_UPDATE_INTERVAL, DOMAIN
from .coordinator import FreeSleepCoordinator
from .logger import log
from .pod import Pod
from .services import register_services

# This tells Home Assistant that the integration can only be set up via config
# entries (i.e., through the UI) and not through YAML configuration.
CONFIG_SCHEMA = config_entry_only_config_schema(DOMAIN)

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
  api = FreeSleepAPI(entry.data.get(CONF_HOST), async_get_clientsession(hass))
  coordinator = FreeSleepCoordinator(
    hass,
    log,
    api,
    update_interval=entry.data.get(CONF_UPDATE_INTERVAL, 30),
    config_entry=entry,
  )

  await coordinator.async_config_entry_first_refresh()
  pod = Pod(hass, coordinator, entry, entry.data.get(CONF_HOST))

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
