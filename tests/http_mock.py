"""requests-mock-compatible facade over respx.

Exposes the requests-mock ``Mocker`` API (``@requests_mock.Mocker()``
decorator injecting ``m``, and ``with requests_mock.Mocker() as m``)
on top of respx, so ``m.get(...)`` call sites keep working against the
httpx transport.
"""

import functools
import re

import httpx
import respx


def http_status_error(status_code):
    """Build an httpx.HTTPStatusError carrying the given status code.

    httpx requires request and response objects, unlike the
    ``requests.HTTPError(response=Mock(status_code=...))`` idiom.
    """
    request = httpx.Request("GET", "https://www.basketball-reference.com")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError(f"HTTP {status_code}", request=request, response=response)


class Mocker:
    def __init__(self):
        self._router = None

    def get(self, url, text="", status_code=200, json=None, headers=None, complete_qs=False):
        # complete_qs is accepted for requests-mock API compatibility; respx
        # already matches query strings exactly when the URL includes one.
        del complete_qs
        if self._router is None:
            raise RuntimeError("Mocker must be active (used as a context manager) before registering routes")
        # requests-mock collapsed duplicate slashes when matching; respx is
        # exact. Normalize registrations so "BASE_URL//path" entries
        # still match the single-slash URLs the client requests.
        parsed = httpx.URL(url)
        if "//" in parsed.path:
            url = str(parsed.copy_with(path=re.sub(r"/{2,}", "/", parsed.path)))
        if json is not None:
            response = httpx.Response(status_code, json=json, headers=headers)
        else:
            response = httpx.Response(status_code, text=text, headers=headers)
        self._router.get(url).mock(return_value=response)

    @property
    def call_count(self):
        if self._router is None:
            return 0
        return self._router.calls.call_count

    def __enter__(self):
        self._router = respx.mock(assert_all_called=False)
        self._router.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        router, self._router = self._router, None
        if router is None:
            return False
        return router.__exit__(exc_type, exc, tb)

    def __call__(self, obj):
        # requests-mock supports decorating a TestCase class, which wraps
        # every ``test*`` method. Without this branch the class would be
        # replaced by a plain function and pytest would silently skip it.
        if isinstance(obj, type):
            for name in dir(obj):
                if name.startswith("test") and callable(getattr(obj, name)):
                    setattr(obj, name, self(getattr(obj, name)))
            return obj

        @functools.wraps(obj)
        def wrapper(*args, **kwargs):
            # requests-mock injects the active mocker as the last
            # positional argument; tests rely on that signature.
            with Mocker() as m:
                return obj(*args, m, **kwargs)

        return wrapper
