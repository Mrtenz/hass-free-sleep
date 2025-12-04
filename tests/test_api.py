"""Tests for the API module."""

from typing import Any
from unittest.mock import patch

import pytest
from aiohttp import ClientResponseError
from pytest_httpserver import HTTPServer

from custom_components.free_sleep.api import FreeSleepAPI
from custom_components.free_sleep.constants import PodSide


class MockResponse:
  """
  A mock response object to simulate `aiohttp.ClientResponse`.

  This only contains the parts needed for testing the FreeSleepAPI class.
  """

  def __init__(
    self, json: dict[str, Any] | None = None, status: int = 200
  ) -> None:
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
  ) -> dict[str, Any] | None:
    """
    Get the JSON data from the response.

    :param content_type: The content type of the response.
    :return: The JSON data.
    """
    return self._json


async def test_parse_response_no_content(api: FreeSleepAPI) -> None:
  """Test parsing a 204 No Content response."""
  response = MockResponse(status=204)
  result = await api.parse_response(response)

  assert result == {}


async def test_parse_response_with_content(api: FreeSleepAPI) -> None:
  """Test parsing a response with JSON content."""
  json_data = {'key': 'value'}
  response = MockResponse(status=200, json=json_data)
  result = await api.parse_response(response)

  assert result == json_data


async def test_get_request(api: FreeSleepAPI, httpserver: HTTPServer) -> None:
  """Test sending a GET request."""
  httpserver.expect_request('/test').respond_with_json({'message': 'success'})

  result = await api.get(httpserver.url_for('/test'))
  assert result == {'message': 'success'}


async def test_get_request_with_params(
  api: FreeSleepAPI, httpserver: HTTPServer
) -> None:
  """Test sending a GET request with query parameters."""
  httpserver.expect_request(
    '/test', query_string={'param1': 'value1', 'param2': 'value2'}
  ).respond_with_json({'message': 'params received'})

  result = await api.get(
    httpserver.url_for('/test'), params={'param1': 'value1', 'param2': 'value2'}
  )
  assert result == {'message': 'params received'}


async def test_get_request_no_content(
  api: FreeSleepAPI, httpserver: HTTPServer
) -> None:
  """Test sending a GET request that returns no content."""
  httpserver.expect_request('/test').respond_with_data('', status=204)

  result = await api.get(httpserver.url_for('/test'))
  assert result == {}


async def test_get_request_raise_for_status(
  api: FreeSleepAPI, httpserver: HTTPServer
) -> None:
  """Test that a GET request raises for non-200 status codes."""
  httpserver.expect_request('/test').respond_with_data('Not Found', status=404)

  with pytest.raises(ClientResponseError):
    await api.get(httpserver.url_for('/test'))


async def test_post_request(api: FreeSleepAPI, httpserver: HTTPServer) -> None:
  """Test sending a POST request."""
  json_data = {'data': 'value'}
  httpserver.expect_request(
    '/test', method='POST', json=json_data
  ).respond_with_json({'status': 'created'})

  result = await api.post(httpserver.url_for('/test'), json_data=json_data)
  assert result == {'status': 'created'}


async def test_post_request_no_content(
  api: FreeSleepAPI, httpserver: HTTPServer
) -> None:
  """Test sending a POST request that returns no content."""
  json_data = {'data': 'value'}
  httpserver.expect_request(
    '/test', method='POST', json=json_data
  ).respond_with_data('', status=204)

  result = await api.post(httpserver.url_for('/test'), json_data=json_data)
  assert result == {}


async def test_post_request_raise_for_status(
  api: FreeSleepAPI, httpserver: HTTPServer
) -> None:
  """Test that a POST request raises for non-200 status codes."""
  json_data = {'data': 'value'}
  httpserver.expect_request(
    '/test', method='POST', json=json_data
  ).respond_with_data('Bad Request', status=400)

  with pytest.raises(ClientResponseError):
    await api.post(httpserver.url_for('/test'), json_data=json_data)


async def test_fetch_device_status(
  api: FreeSleepAPI, mock_device_status: dict[str, Any], httpserver: HTTPServer
) -> None:
  """Test fetching device status."""
  httpserver.expect_request('/api/deviceStatus').respond_with_json(
    mock_device_status
  )

  result = await api.fetch_device_status()
  assert result == mock_device_status


async def test_fetch_settings(
  api: FreeSleepAPI, mock_settings: dict[str, Any], httpserver: HTTPServer
) -> None:
  """Test fetching device settings."""
  httpserver.expect_request('/api/settings').respond_with_json(mock_settings)

  result = await api.fetch_settings()
  assert result == mock_settings


async def test_fetch_services(
  api: FreeSleepAPI, mock_services: dict[str, Any], httpserver: HTTPServer
) -> None:
  """Test fetching device services."""
  httpserver.expect_request('/api/services').respond_with_json(mock_services)

  result = await api.fetch_services()
  assert result == mock_services


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
  httpserver: HTTPServer,
  side: PodSide,
) -> None:
  """Test fetching device vitals."""
  httpserver.expect_request(
    '/api/metrics/vitals/summary', query_string={'side': side}
  ).respond_with_json(mock_vitals)

  result = await api.fetch_vitals(side)
  assert result == mock_vitals


async def test_fetch_current_version(
  api: FreeSleepAPI, mock_device_status: dict[str, Any], httpserver: HTTPServer
) -> None:
  """Test fetching current firmware version."""
  httpserver.expect_request('/api/deviceStatus').respond_with_json(
    mock_device_status
  )

  result = await api.fetch_current_version()
  assert result == '2.1.3'


async def test_fetch_latest_version(
  api: FreeSleepAPI,
  mock_latest_version: dict[str, Any],
  httpserver: HTTPServer,
) -> None:
  """Test fetching latest firmware version."""
  httpserver.expect_request(
    '/custom/github/server-info.json'
  ).respond_with_json(mock_latest_version)

  with patch(
    'custom_components.free_sleep.api.SERVER_INFO_URL',
    httpserver.url_for('/custom/github/server-info.json'),
  ):
    result = await api.fetch_latest_version()
    assert result == '2.2.0'


async def test_update_device_status(
  api: FreeSleepAPI,
  httpserver: HTTPServer,
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

  httpserver.expect_request(
    '/api/deviceStatus', method='POST', json=json_data
  ).respond_with_data('', status=204)

  await api.update_device_status(json_data)


async def test_update_settings(
  api: FreeSleepAPI,
  httpserver: HTTPServer,
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

  httpserver.expect_request(
    '/api/settings', method='POST', json=json_data
  ).respond_with_data('', status=204)

  await api.update_settings(json_data)


async def test_update_schedule(
  api: FreeSleepAPI,
  httpserver: HTTPServer,
) -> None:
  """Test updating sleep schedule."""
  json_data = {
    'left': {
      'alarm': {'alarmTemperature': 68},
      'power': {'onTemperature': 72},
      'temperatures': {'08:00': 65, '20:00': 70},
    }
  }

  httpserver.expect_request(
    '/api/schedules', method='POST', json=json_data
  ).respond_with_data('', status=204)

  await api.update_schedule(json_data)


async def test_update_services(
  api: FreeSleepAPI,
  httpserver: HTTPServer,
) -> None:
  """Test updating device services."""
  json_data = {
    'biometrics': {'enabled': True},
  }

  httpserver.expect_request(
    '/api/services', method='POST', json=json_data
  ).respond_with_data('', status=204)

  await api.update_services(json_data)


async def test_execute(
  api: FreeSleepAPI,
  httpserver: HTTPServer,
) -> None:
  """Test executing a command on the device."""
  json_data = {
    'command': 'HELLO',
  }

  httpserver.expect_request(
    '/api/execute', method='POST', json=json_data
  ).respond_with_json({'status': 'ok'})

  result = await api.execute(json_data)
  assert result == {'status': 'ok'}


async def test_run_jobs(
  api: FreeSleepAPI,
  httpserver: HTTPServer,
) -> None:
  """Test running jobs on the device."""
  jobs = ['job1', 'job2']

  httpserver.expect_request(
    '/api/jobs', method='POST', json=jobs
  ).respond_with_data('', status=204)

  await api.run_jobs(jobs)
