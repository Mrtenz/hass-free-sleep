"""Constants for the Free Sleep integration."""

from typing import Final, Literal

DOMAIN: Final = 'free_sleep'

DEVICE_STATUS_ENDPOINT = '/api/deviceStatus'
SETTINGS_ENDPOINT = '/api/settings'
VITALS_SUMMARY_ENDPOINT = '/api/metrics/vitals/summary'

EIGHT_SLEEP_MIN_TEMPERATURE_F: Final = 55
EIGHT_SLEEP_MAX_TEMPERATURE_F: Final = 110
EIGHT_SLEEP_TEMPERATURE_STEP_F: Final = 0.5

PodSide = Literal['left', 'right']
