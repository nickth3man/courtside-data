"""requests-mock-compatible facade over respx.

The test suite was written against requests-mock's ``Mocker`` API
(``@requests_mock.Mocker()`` decorator injecting ``m``, and
``with requests_mock.Mocker() as m``). After the requests -> httpx
migration, this shim preserves that API on top of respx so the ~160
existing ``m.get(...)`` call sites stay untouched.
"""
import functools

import httpx
import respx


def http_status_error(status_code):
    """Build an httpx.HTTPStatusError carrying the given status code.

    Replaces the old ``requests.HTTPError(response=Mock(status_code=...))``
    test idiom; httpx requires request and response objects.
    """
    request = httpx.Request("GET", "https://www.basketball-reference.com")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError(f"HTTP {status_code}", request=request, response=response)


class Mocker:
    def __init__(self):
        self._router = None

    def get(self, url, text="", status_code=200, json=None, headers=None):
        if self._router is None:
            raise RuntimeError("Mocker must be active (used as a context manager) before registering routes")
        if json is not None:
            response = httpx.Response(status_code, json=json, headers=headers)
        else:
            response = httpx.Response(status_code, text=text, headers=headers)
        self._router.get(url).mock(return_value=response)

    def __enter__(self):
        self._router = respx.mock(assert_all_called=False)
        self._router.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        router, self._router = self._router, None
        return router.__exit__(exc_type, exc, tb)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # requests-mock injects the active mocker as the last
            # positional argument; tests rely on that signature.
            with Mocker() as m:
                return func(*args, m, **kwargs)

        return wrapper
