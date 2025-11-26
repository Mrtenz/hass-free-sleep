"""Utility functions used in the Free Sleep integration."""

from homeassistant.const import UnitOfTemperature


def unit_to_fahrenheit(unit: UnitOfTemperature, value: float) -> int:
  """
  Convert a temperature value to Fahrenheit for the given unit (Celsius, Kelvin,
  or Fahrenheit), rounded to the nearest integer.

  :param unit: The current unit of temperature.
  :param value: The temperature value to convert.
  :return: The temperature value in Fahrenheit.
  """
  if unit == UnitOfTemperature.FAHRENHEIT:
    return round(value)

  celsius_value = value - 273.15 if unit == UnitOfTemperature.KELVIN else value
  return round((celsius_value * 1.8) + 32)


def schedule_to_fahrenheit(unit: UnitOfTemperature, schedule: dict) -> dict:
  """
  Convert temperature values in a schedule to Fahrenheit. If the unit is already
  Fahrenheit, the schedule is returned unchanged.

  This is useful since the Free Sleep API expects temperatures in Fahrenheit,
  but the user may provide temperatures in Celsius (or Kelvin), depending on
  their Home Assistant configuration.

  :param unit: The current unit of temperature (Celsius or Fahrenheit).
  :param schedule: The schedule dictionary with temperature values.
  :return: A new schedule dictionary with temperatures in Fahrenheit.
  """
  if unit == UnitOfTemperature.FAHRENHEIT:
    return schedule

  converted_schedule = {**schedule}

  if (alarm := schedule.get('alarm')) and 'alarmTemperature' in alarm:
    converted_schedule['alarm']['alarmTemperature'] = unit_to_fahrenheit(
      unit, alarm['alarmTemperature']
    )

  if (power := schedule.get('power')) and 'onTemperature' in power:
    converted_schedule['power']['onTemperature'] = unit_to_fahrenheit(
      unit, power['onTemperature']
    )

  if temperatures := schedule.get('temperatures'):
    converted_schedule['temperatures'] = {
      time: unit_to_fahrenheit(unit, temperature)
      for time, temperature in temperatures.items()
    }

  return converted_schedule
