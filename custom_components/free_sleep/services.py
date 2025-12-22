"""
Services for the Free Sleep Pod integration.

This module defines and registers services that allow users to interact
with their Free Sleep Pod devices, such as setting sleep schedules.
"""

from typing import TypedDict, cast

from homeassistant.core import (
  HomeAssistant,
  ServiceCall,
  ServiceResponse,
  SupportsResponse,
)
from homeassistant.helpers.device_registry import async_get
from voluptuous import In, Optional, Or, Required, Schema

from .constants import (
  DAYS_OF_WEEK,
  DOMAIN,
  EXECUTE_SERVICE,
  SET_SCHEDULE_SERVICE,
)
from .utils import schedule_to_fahrenheit


class ExecuteServiceCallData(TypedDict):
  """Data structure for the execute service call."""

  pod: str
  command: str
  value: str | None


class ExecuteServiceCall(ServiceCall):
  """Service call for executing a command on a pod."""

  data: ExecuteServiceCallData


class SetScheduleServiceCallData(TypedDict):
  """Data structure for the set schedule service call."""

  side: str | list[str]
  day_of_week: str | list[str] | None
  schedule: dict


class SetScheduleServiceCall(ServiceCall):
  """Service call for setting the sleep schedule on a pod side."""

  data: SetScheduleServiceCallData


async def register_services(hass: HomeAssistant) -> None:  # noqa: C901
  """
  Register services for the Free Sleep Pod integration.

  :param hass: The Home Assistant instance.
  """

  async def handle_execute(call: ServiceCall) -> ServiceResponse | None:
    """
    Handle the service call to execute a command.

    :param call: The service call data.
    :raises ValueError: If the specified side device is not found.
    """
    registry = async_get(hass)
    _call = cast('ExecuteServiceCall', call)

    pod_id = _call.data.get('pod')
    command = _call.data.get('command')
    value = _call.data.get('value', '')

    pod = registry.async_get(pod_id)
    if not pod:
      message = f'Device for pod "{pod_id}" not found.'
      raise ValueError(message)

    for entity in hass.data[DOMAIN].values():
      pod_instance, _ = entity
      if pod_instance.device_info.get('identifiers') == pod.identifiers:
        response = await pod_instance.execute_command(command, value)
        if response and call.return_response:
          return response

    return None

  async def handle_set_schedule(call: ServiceCall) -> None:
    """
    Handle the service call to set the sleep schedule.

    :param call: The service call data.
    :raises ValueError: If the specified side device is not found.
    """
    registry = async_get(hass)
    _call = cast('SetScheduleServiceCall', call)

    side_ids = _call.data.get('side')
    if isinstance(side_ids, str):
      side_ids = [side_ids]

    days_of_week = _call.data.get('day_of_week', DAYS_OF_WEEK)
    if isinstance(days_of_week, str):
      days_of_week = [days_of_week]

    schedule = schedule_to_fahrenheit(
      hass.config.units.temperature_unit,
      cast('dict', _call.data.get('schedule')),
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
    EXECUTE_SERVICE,
    handle_execute,
    schema=Schema(
      {
        Required('pod'): str,
        Required('command'): str,
        Optional('value'): str,
      }
    ),
    supports_response=SupportsResponse.OPTIONAL,
  )

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
