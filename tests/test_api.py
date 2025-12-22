"""Tests for the API module."""

from typing import Any, cast
from unittest.mock import patch

import pytest
from aiohttp import ClientResponse, ClientResponseError
from aioresponses import aioresponses

from custom_components.free_sleep.api import FreeSleepAPI
from custom_components.free_sleep.constants import PodSide
from tests.helpers import Json, Url


class MockResponse:
  """
  A mock response object to simulate `aiohttp.ClientResponse`.

  This only contains the parts needed for testing the FreeSleepAPI class.
  """

  def __init__(self, json: Json = None, status: int = 200) -> None:
    """
    Initialize the mock response.

    :param json: The JSON data to return.
    :param status: The HTTP status code of the response.
    """
    self._json = json
    self.status = status

  async def json(
    self,
    content_type: str | None = None,  # noqa: ARG002
  ) -> Json:
    """
    Get the JSON data from the response.

    :param content_type: The content type of the response.
    :return: The JSON data.
    """
    return self._json


async def test_parse_response_no_content(api: FreeSleepAPI) -> None:
  """Test parsing a 204 No Content response."""
  response = MockResponse(status=204)
  client_response = cast('ClientResponse', cast('object', response))

  result = await api.parse_response(client_response)

  assert result == {}


async def test_parse_response_with_content(api: FreeSleepAPI) -> None:
  """Test parsing a response with JSON content."""
  json_data = {'key': 'value'}
  response = MockResponse(status=200, json=json_data)
  client_response = cast('ClientResponse', cast('object', response))

  result = await api.parse_response(client_response)

  assert result == json_data


async def test_get_request(
  api: FreeSleepAPI, http: aioresponses, url: Url
) -> None:
  """Test sending a GET request."""
  http.get(url('/test'), payload={'message': 'success'})

  result = await api.get(url('/test'))
  assert result == {'message': 'success'}
  http.assert_called_with(
    url=url('/test'),
    method='GET',
    params=None,
    timeout=10,
  )


async def test_get_request_with_params(
  api: FreeSleepAPI, http: aioresponses, url: Url
) -> None:
  """Test sending a GET request with query parameters."""
  http.get(
    url('/test?param1=value1&param2=value2'),
    payload={'message': 'params received'},
  )

  result = await api.get(
    url('/test'), params={'param1': 'value1', 'param2': 'value2'}
  )
  assert result == {'message': 'params received'}
  http.assert_called_with(
    url=url('/test'),
    method='GET',
    params={'param1': 'value1', 'param2': 'value2'},
    timeout=10,
  )


async def test_get_request_no_content(
  api: FreeSleepAPI, http: aioresponses, url: Url
) -> None:
  """Test sending a GET request that returns no content."""
  http.get(url('/test'), status=204)

  result = await api.get(url('/test'))
  assert result == {}
  http.assert_called_with(
    url=url('/test'),
    method='GET',
    params=None,
    timeout=10,
  )


async def test_get_request_raise_for_status(
  api: FreeSleepAPI, http: aioresponses, url: Url
) -> None:
  """Test that a GET request raises for non-200 status codes."""
  http.get(url('/test'), status=404)

  with pytest.raises(ClientResponseError):
    await api.get(url('/test'))
  http.assert_called_with(
    url=url('/test'),
    method='GET',
    params=None,
    timeout=10,
  )


async def test_post_request(
  api: FreeSleepAPI, http: aioresponses, url: Url
) -> None:
  """Test sending a POST request."""
  json_data = {'data': 'value'}
  http.post(url('/test'), payload={'status': 'created'})

  result = await api.post(url('/test'), json_data=json_data)
  assert result == {'status': 'created'}
  http.assert_called_with(
    url=url('/test'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_post_request_no_content(
  api: FreeSleepAPI, http: aioresponses, url: Url
) -> None:
  """Test sending a POST request that returns no content."""
  json_data = {'data': 'value'}
  http.post(url('/test'), status=204)

  result = await api.post(url('/test'), json_data=json_data)
  assert result == {}
  http.assert_called_with(
    url=url('/test'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_post_request_raise_for_status(
  api: FreeSleepAPI, http: aioresponses, url: Url
) -> None:
  """Test that a POST request raises for non-200 status codes."""
  json_data = {'data': 'value'}
  http.post(url('/test'), status=400)

  with pytest.raises(ClientResponseError):
    await api.post(url('/test'), json_data=json_data)
  http.assert_called_with(
    url=url('/test'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_fetch_device_status(
  api: FreeSleepAPI,
  mock_device_status: dict[str, Any],
  http: aioresponses,
  url: Url,
) -> None:
  """Test fetching device status."""
  http.get(url('/api/deviceStatus'), payload=mock_device_status)

  result = await api.fetch_device_status()
  assert result == mock_device_status
  http.assert_called_with(
    url=url('/api/deviceStatus'),
    method='GET',
    params=None,
    timeout=10,
  )


async def test_fetch_settings(
  api: FreeSleepAPI,
  mock_settings: dict[str, Any],
  http: aioresponses,
  url: Url,
) -> None:
  """Test fetching device settings."""
  http.get(url('/api/settings'), payload=mock_settings)

  result = await api.fetch_settings()
  assert result == mock_settings
  http.assert_called_with(
    url=url('/api/settings'),
    method='GET',
    params=None,
    timeout=10,
  )


async def test_fetch_services(
  api: FreeSleepAPI,
  mock_services: dict[str, Any],
  http: aioresponses,
  url: Url,
) -> None:
  """Test fetching device services."""
  http.get(url('/api/services'), payload=mock_services)

  result = await api.fetch_services()
  assert result == mock_services
  http.assert_called_with(
    url=url('/api/services'),
    method='GET',
    params=None,
    timeout=10,
  )


@pytest.mark.parametrize(
  'side',
  [
    'left',
    'right',
  ],
)
async def test_fetch_vitals(
  api: FreeSleepAPI,
  mock_vitals: dict[str, Any],
  http: aioresponses,
  url: Url,
  side: PodSide,
) -> None:
  """Test fetching device vitals."""
  http.get(url(f'/api/metrics/vitals/summary?side={side}'), payload=mock_vitals)

  result = await api.fetch_vitals(side)
  assert result == mock_vitals
  http.assert_called_with(
    url=url('/api/metrics/vitals/summary'),
    method='GET',
    params={'side': side},
    timeout=10,
  )


async def test_fetch_presence(
  api: FreeSleepAPI,
  mock_presence: dict[str, Any],
  http: aioresponses,
  url: Url,
) -> None:
  """Test fetching presence data."""
  http.get(url('/api/metrics/presence'), payload=mock_presence)

  result = await api.fetch_presence()
  assert result == mock_presence
  http.assert_called_with(
    url=url('/api/metrics/presence'),
    method='GET',
    params=None,
    timeout=10,
  )


async def test_fetch_current_version(
  api: FreeSleepAPI,
  mock_device_status: dict[str, Any],
  http: aioresponses,
  url: Url,
) -> None:
  """Test fetching current firmware version."""
  http.get(url('/api/deviceStatus'), payload=mock_device_status)

  result = await api.fetch_current_version()
  assert result == '2.1.3'
  http.assert_called_with(
    url=url('/api/deviceStatus'),
    method='GET',
    params=None,
    timeout=10,
  )


async def test_fetch_latest_version(
  api: FreeSleepAPI,
  mock_latest_version: dict[str, Any],
  http: aioresponses,
  url: Url,
) -> None:
  """Test fetching latest firmware version."""
  http.get(url('/custom/github/server-info.json'), payload=mock_latest_version)

  with patch(
    'custom_components.free_sleep.api.SERVER_INFO_URL',
    url('/custom/github/server-info.json'),
  ):
    result = await api.fetch_latest_version()
    assert result == '2.2.0'
    http.assert_called_with(
      url=url('/custom/github/server-info.json'),
      method='GET',
      params=None,
      timeout=10,
    )


async def test_update_device_status(
  api: FreeSleepAPI,
  http: aioresponses,
  url: Url,
) -> None:
  """Test updating device status."""
  json_data = {
    'left': {
      'targetTemperatureF': 70,
      'isOn': True,
    },
    'right': {
      'targetTemperatureF': 75,
      'isOn': False,
    },
  }

  http.post(url('/api/deviceStatus'), status=204)

  await api.update_device_status(json_data)
  http.assert_called_with(
    url=url('/api/deviceStatus'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_update_settings(
  api: FreeSleepAPI,
  http: aioresponses,
  url: Url,
) -> None:
  """Test updating device settings."""
  json_data = {
    'timeZone': 'America/New_York',
    'left': {
      'name': 'Left Pod',
      'awayMode': True,
    },
    'right': {
      'name': 'Right Pod',
      'awayMode': False,
    },
  }

  http.post(url('/api/settings'), status=204)

  await api.update_settings(json_data)
  http.assert_called_with(
    url=url('/api/settings'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_update_schedule(
  api: FreeSleepAPI,
  http: aioresponses,
  url: Url,
) -> None:
  """Test updating sleep schedule."""
  json_data = {
    'left': {
      'alarm': {'alarmTemperature': 68},
      'power': {'onTemperature': 72},
      'temperatures': {'08:00': 65, '20:00': 70},
    }
  }

  http.post(url('/api/schedules'), status=204)

  await api.update_schedule(json_data)
  http.assert_called_with(
    url=url('/api/schedules'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_update_services(
  api: FreeSleepAPI,
  http: aioresponses,
  url: Url,
) -> None:
  """Test updating device services."""
  json_data = {
    'biometrics': {'enabled': True},
  }

  http.post(url('/api/services'), status=204)

  await api.update_services(json_data)
  http.assert_called_with(
    url=url('/api/services'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_execute(
  http: aioresponses,
  url: Url,
  api: FreeSleepAPI,
) -> None:
  """Test executing a command on the device."""
  json_data = {
    'command': 'HELLO',
  }

  http.post(url('/api/execute'), payload={'status': 'ok'})

  result = await api.execute(json_data)
  assert result == {'status': 'ok'}
  http.assert_called_with(
    url=url('/api/execute'),
    method='POST',
    json=json_data,
    timeout=10,
  )


async def test_run_jobs(
  http: aioresponses,
  url: Url,
  api: FreeSleepAPI,
) -> None:
  """Test running jobs on the device."""
  jobs = ['job1', 'job2']

  http.post(url('/api/jobs'), status=204)

  await api.run_jobs(jobs)
  http.assert_called_with(
    url=url('/api/jobs'),
    method='POST',
    json=jobs,
    timeout=10,
  )
