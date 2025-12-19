"""
Config flow for Free Sleep Pod integration.

This is loaded by Home Assistant to handle the configuration flow
for the Free Sleep Pod integration.
"""

from typing import Any

import voluptuous
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FreeSleepAPI
from .constants import CONF_UPDATE_INTERVAL, DOMAIN
from .logger import log

HOST_SCHEMA = voluptuous.Schema(
  {
    voluptuous.Required(
      CONF_HOST,
    ): str,
    voluptuous.Optional(
      CONF_UPDATE_INTERVAL,
      default=30,
    ): voluptuous.All(voluptuous.Coerce(int), voluptuous.Range(min=5, max=300)),
  }
)


async def validate_connection(url: str, hass: HomeAssistant) -> str:
  """
  Validate the connection to the Free Sleep Pod device, and return the name of
  the device if successful.

  :param url: The URL of the Free Sleep Pod device.
  :param hass: The Home Assistant instance.
  :return: The hub version of the device.
  :raises ConnectionError: connection error
  """
  api = FreeSleepAPI(url, async_get_clientsession(hass))
  try:
    status = await api.fetch_device_status()
    return status['hubVersion']
  except Exception as e:
    log.error(f'Connection validation failed: {e}')
    raise ValueError('cannot_connect') from e


async def validate_setup(
  user_input: dict[str, Any], hass: HomeAssistant
) -> tuple[str, dict[str, Any]]:
  """
  Validate the user input for the config flow.

  :param user_input: The user input from the config flow form.
  :param hass: The Home Assistant instance.
  """
  url = user_input[CONF_HOST]
  if not (url.startswith(('http://', 'https://'))):
    raise ValueError('invalid_url')

  name = await validate_connection(url, hass)

  return name, user_input


class FreeSleepConfigFlow(ConfigFlow, domain=DOMAIN):
  """The config flow for the Free Sleep Pod integration."""

  VERSION = 0
  MINOR_VERSION = 1

  async def async_step_user(
    self, user_input: dict[str, Any] | None = None
  ) -> ConfigFlowResult:
    """
    Initiate the integration config flow.

    This is invoked when the user starts the configuration process
    for the Free Sleep Pod integration from the Home Assistant UI.
    """
    errors: dict[str, str] = {}

    if user_input is not None:
      try:
        name, data = await validate_setup(user_input, self.hass)
      except ValueError as error:
        errors[CONF_HOST] = str(error)

      if not errors:
        return self.async_create_entry(
          title=name,
          data=data,
        )

    return self.async_show_form(
      step_id='user', data_schema=HOST_SCHEMA, errors=errors
    )
