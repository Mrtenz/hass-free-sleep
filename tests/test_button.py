"""Tests for Free Sleep button entities."""

from aioresponses import aioresponses
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.free_sleep.constants import (
  DEVICE_STATUS_ENDPOINT,
  JOBS_ENDPOINT,
)
from tests.helpers import AssertPost, Url


async def test_button_prime(
  hass: HomeAssistant,
  integration: MockConfigEntry,  # noqa: ARG001
  http: aioresponses,
  url: Url,
  assert_post: AssertPost,
) -> None:
  """Test `button.pod_4_prime`."""
  button = hass.states.get('button.pod_4_prime')

  assert button is not None
  assert button.state == 'unknown'
  assert button.attributes.get('friendly_name') == 'Pod 4 Prime'
  assert button.attributes.get('icon') == 'mdi:water-pump'

  http.post(
    url(DEVICE_STATUS_ENDPOINT),
    payload={},
    status=204,
  )

  await hass.services.async_call(
    BUTTON_DOMAIN,
    SERVICE_PRESS,
    {
      ATTR_ENTITY_ID: 'button.pod_4_prime',
    },
    blocking=True,
  )
  await hass.async_block_till_done()

  assert_post(
    url(DEVICE_STATUS_ENDPOINT),
    {
      'isPriming': True,
    },
  )


async def test_button_reboot(
  hass: HomeAssistant,
  integration: MockConfigEntry,  # noqa: ARG001
  http: aioresponses,
  url: Url,
  assert_post: AssertPost,
) -> None:
  """Test `button.pod_4_reboot`."""
  button = hass.states.get('button.pod_4_reboot')

  assert button is not None
  assert button.state == 'unknown'
  assert button.attributes.get('friendly_name') == 'Pod 4 Reboot'
  assert button.attributes.get('icon') == 'mdi:restart'

  http.post(
    url(JOBS_ENDPOINT),
    payload={},
    status=204,
  )

  await hass.services.async_call(
    BUTTON_DOMAIN,
    SERVICE_PRESS,
    {
      ATTR_ENTITY_ID: 'button.pod_4_reboot',
    },
    blocking=True,
  )
  await hass.async_block_till_done()

  assert_post(
    url(JOBS_ENDPOINT),
    ['reboot'],
  )
