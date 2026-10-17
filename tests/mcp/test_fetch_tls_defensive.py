# Copyright (c) 2026 Carlos Felipe. SPDX-License-Identifier: MIT
"""Mock-only transport checks for explicit TLS policy and fail-closed errors."""

import httpx
import pytest

from vulnclaw.config.schema import VulnClawConfig
from vulnclaw.mcp.lifecycle import MCPLifecycleManager


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, True), (True, True), (False, False), ("true", True),
     ("false", False), ("invalid", True)],
)
async def test_fetch_tls_policy_reaches_client(monkeypatch, value, expected):
    seen = []

    class Client(httpx.AsyncClient):
        def __init__(self, **kwargs):
            seen.append(kwargs["verify"])
            kwargs["transport"] = httpx.MockTransport(lambda request: httpx.Response(200, text="ok"))
            super().__init__(**kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", Client)
    manager = MCPLifecycleManager(VulnClawConfig())
    args = {"url": "https://fixture.invalid/"}
    if value is not None:
        args["verify_tls"] = value
    result = await manager._call_fetch(args)
    assert "Status: 200" in result
    assert seen == [expected]


@pytest.mark.parametrize("explicit", [False, True])
async def test_certificate_failure_never_returns_unverified_body(monkeypatch, explicit):
    seen = []

    def handler(request):
        if seen[-1]:
            raise httpx.ConnectError("CERTIFICATE_VERIFY_FAILED", request=request)
        return httpx.Response(200, text="UNVERIFIED_FIXTURE_BODY")

    class Client(httpx.AsyncClient):
        def __init__(self, **kwargs):
            seen.append(kwargs["verify"])
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(**kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", Client)
    manager = MCPLifecycleManager(VulnClawConfig())
    args = {"url": "https://fixture.invalid/"}
    if explicit:
        args["verify_tls"] = True
    result = await manager._call_fetch(args)
    assert seen == [True]
    assert "CERTIFICATE_VERIFY_FAILED" in result
    assert "UNVERIFIED_FIXTURE_BODY" not in result
