"""Constants for the Free Sleep integration."""

from typing import Final, Literal

DOMAIN: Final = 'free_sleep'

SET_SCHEDULE_SERVICE: Final = 'set_schedule'

DEVICE_STATUS_ENDPOINT: Final = '/api/deviceStatus'
JOBS_ENDPOINT: Final = '/api/jobs'
SETTINGS_ENDPOINT: Final = '/api/settings'
SCHEDULES_ENDPOINT: Final = '/api/schedules'
VITALS_SUMMARY_ENDPOINT: Final = '/api/metrics/vitals/summary'

SERVER_INFO_URL: Final = 'https://raw.githubusercontent.com/throwaway31265/free-sleep/refs/heads/main/server/src/serverInfo.json'

EIGHT_SLEEP_MIN_TEMPERATURE_F: Final = 55
EIGHT_SLEEP_MAX_TEMPERATURE_F: Final = 110
EIGHT_SLEEP_TEMPERATURE_STEP_F: Final = 0.5

PodSide = Literal['left', 'right']

DAYS_OF_WEEK: Final = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]
