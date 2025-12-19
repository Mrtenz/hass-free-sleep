"""Tests for the config flow module."""

import logging
from collections.abc import Callable, Generator
from unittest.mock import patch

import pytest
from aioresponses import aioresponses
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.free_sleep.config_flow import (
  validate_connection,
  validate_setup,
)
from custom_components.free_sleep.constants import (
  DEVICE_STATUS_ENDPOINT,
  DOMAIN,
)


@pytest.fixture(autouse=True)
def configure_logging(caplog: pytest.LogCaptureFixture) -> None:
  """
  Configure logging for the tests to only show errors by default.

  Behaviour can be overridden in individual tests using the `caplog` fixture.
  """
  caplog.set_level(logging.ERROR)


@pytest.fixture(autouse=True)
def skip_setup() -> Generator[None]:
  """Skip setup of the integration."""
  with (
    patch('custom_components.free_sleep.async_setup', return_value=True),
    patch(
      'custom_components.free_sleep.async_setup_entry',
      return_value=True,
    ),
    patch('custom_components.free_sleep.async_unload_entry', return_value=True),
  ):
    yield


async def test_validate_connection(
  http: aioresponses, url: Callable[[str], str], hass: HomeAssistant
) -> None:
  """Test the `validate_connection` function."""
  http.get(
    url(DEVICE_STATUS_ENDPOINT),
    payload={
      'hubVersion': '1.2.3',
    },
  )

  result = await validate_connection(url(), hass)
  assert result == '1.2.3'


async def test_validate_connection_failure(
  http: aioresponses,
  url: Callable[[str], str],
  hass: HomeAssistant,
  caplog: pytest.LogCaptureFixture,
) -> None:
  """Test the `validate_connection` function for failure."""
  caplog.set_level(logging.CRITICAL)
  http.get(url(DEVICE_STATUS_ENDPOINT), status=500)

  with pytest.raises(ValueError, match='cannot_connect'):
    await validate_connection(url(), hass)


async def test_validate_setup(
  http: aioresponses, url: Callable[[str], str], hass: HomeAssistant
) -> None:
  """Test the `validate_setup` function."""
  http.get(
    url(DEVICE_STATUS_ENDPOINT),
    payload={
      'hubVersion': '1.2.3',
    },
  )

  user_input = {
    CONF_HOST: url(),
  }

  name, config = await validate_setup(user_input, hass)
  assert name == '1.2.3'
  assert config == user_input


@pytest.mark.parametrize(
  'input_url', ['invalid_url', 'ftp://example.com', 'www.example.com']
)
async def test_validate_setup_invalid_url(
  hass: HomeAssistant,
  input_url: str,
  caplog: pytest.LogCaptureFixture,
) -> None:
  """Test the `validate_setup` function for invalid URL."""
  caplog.set_level(logging.CRITICAL)

  user_input = {
    CONF_HOST: input_url,
  }

  with pytest.raises(ValueError, match='invalid_url'):
    await validate_setup(user_input, hass)


async def test_validate_setup_failure(
  http: aioresponses, url: Callable[[str], str], hass: HomeAssistant
) -> None:
  """Test the `validate_setup` function for connection failure."""
  http.get(url(DEVICE_STATUS_ENDPOINT), status=500)

  user_input = {
    CONF_HOST: url(),
  }

  with pytest.raises(ValueError, match='cannot_connect'):
    await validate_setup(user_input, hass)


async def test_config_flow(
  hass: HomeAssistant,
  url: Callable[[str], str],
  http: aioresponses,
  enable_custom_integrations: None,  # noqa: ARG001
) -> None:
  """Test the config flow."""
  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={'source': SOURCE_USER}
  )

  assert result['type'] == FlowResultType.FORM
  assert result['step_id'] == 'user'

  http.get(
    url(DEVICE_STATUS_ENDPOINT),
    payload={
      'hubVersion': '1.2.3',
    },
    repeat=True,
  )

  result = await hass.config_entries.flow.async_configure(
    result['flow_id'],
    {'host': url()},
  )

  assert result['type'] == FlowResultType.CREATE_ENTRY
  assert result['title'] == '1.2.3'
  assert result['data'] == {'host': url(), 'update_interval': 30}


async def test_config_flow_custom_update_interval(
  hass: HomeAssistant,
  url: Callable[[str], str],
  http: aioresponses,
  enable_custom_integrations: None,  # noqa: ARG001
) -> None:
  """Test the config flow."""
  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={'source': SOURCE_USER}
  )

  assert result['type'] == FlowResultType.FORM
  assert result['step_id'] == 'user'

  http.get(
    url(DEVICE_STATUS_ENDPOINT),
    payload={
      'hubVersion': '1.2.3',
    },
    repeat=True,
  )

  result = await hass.config_entries.flow.async_configure(
    result['flow_id'],
    {'host': url(), 'update_interval': 45},
  )

  assert result['type'] == FlowResultType.CREATE_ENTRY
  assert result['title'] == '1.2.3'
  assert result['data'] == {'host': url(), 'update_interval': 45}


async def test_config_flow_failure(
  hass: HomeAssistant,
  url: Callable[[str], str],
  http: aioresponses,
  enable_custom_integrations: None,  # noqa: ARG001
) -> None:
  """Test the config flow for connection failure."""
  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={'source': SOURCE_USER}
  )

  assert result['type'] == FlowResultType.FORM
  assert result['step_id'] == 'user'

  http.get(url(DEVICE_STATUS_ENDPOINT), status=500, repeat=True)

  result = await hass.config_entries.flow.async_configure(
    result['flow_id'],
    {CONF_HOST: url()},
  )

  assert result['type'] == FlowResultType.FORM
  assert result['step_id'] == 'user'
  assert result['errors'] == {CONF_HOST: 'cannot_connect'}


async def test_config_flow_invalid_param(
  hass: HomeAssistant,
  enable_custom_integrations: None,  # noqa: ARG001
) -> None:
  """Test the config flow for invalid URL parameter."""
  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={'source': SOURCE_USER}
  )

  assert result['type'] == FlowResultType.FORM
  assert result['step_id'] == 'user'

  result = await hass.config_entries.flow.async_configure(
    result['flow_id'],
    {CONF_HOST: 'invalid_url'},
  )

  assert result['type'] == FlowResultType.FORM
  assert result['step_id'] == 'user'
  assert result['errors'] == {CONF_HOST: 'invalid_url'}
