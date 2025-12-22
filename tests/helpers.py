"""Helper protocols and type definitions for testing."""

from typing import Protocol

# A recursive type definition for JSON-compatible data structures.
type Json = dict[str, Json] | list[Json] | str | int | float | bool | None


class Url(Protocol):
  """Callable protocol to generate full URLs for testing."""

  def __call__(self, url: str | None = None) -> str:
    """Generate a full URL for the given endpoint, or base URL if None."""
    ...


class AssertPost(Protocol):
  """Callable protocol to assert POST requests in tests."""

  def __call__(self, url: str, json: Json = None, requests: int = 1) -> None:
    """
    Assert that a POST request was made to the given URL with expected JSON
    data.
    """
    ...
