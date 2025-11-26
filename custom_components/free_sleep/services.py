"""
Services for the Free Sleep Pod integration.

This module defines and registers services that allow users to interact
with their Free Sleep Pod devices, such as setting sleep schedules.
"""

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.device_registry import async_get
from voluptuous import In, Optional, Or, Required, Schema

from .constants import DAYS_OF_WEEK, DOMAIN, SET_SCHEDULE_SERVICE
from .utils import schedule_to_fahrenheit


async def register_services(hass: HomeAssistant) -> None:
  """
  Register services for the Free Sleep Pod integration.

  :param hass: The Home Assistant instance.
  """

  async def handle_set_schedule(call: ServiceCall) -> None:
    """
    Handle the service call to set the sleep schedule.

    :param call: The service call data.
    :raises ValueError: If the specified side device is not found.
    """
    registry = async_get(hass)

    side_ids = call.data.get('side')
    if isinstance(side_ids, str):
      side_ids = [side_ids]

    days_of_week = call.data.get('day_of_week', DAYS_OF_WEEK)
    if isinstance(days_of_week, str):
      days_of_week = [days_of_week]

    schedule = schedule_to_fahrenheit(
      hass.config.units.temperature_unit, call.data.get('schedule')
    )

    for side_id in side_ids:
      side = registry.async_get(side_id)
      if not side:
        message = f'Device for side "{side_id}" not found.'
        raise ValueError(message)

      for entity in hass.data[DOMAIN].values():
        pod, _ = entity
        for pod_side in pod.sides:
          if pod_side.device_info.get('identifiers') == side.identifiers:
            await pod_side.set_schedule(
              days_of_week=days_of_week,
              schedule=schedule,
            )
            continue

  hass.services.async_register(
    DOMAIN,
    SET_SCHEDULE_SERVICE,
    handle_set_schedule,
    schema=Schema(
      {
        Required('side'): Or(str, [str]),
        Optional('day_of_week'): Or(In(DAYS_OF_WEEK), [In(DAYS_OF_WEEK)]),
        Required('schedule'): dict,
      }
    ),
  )
