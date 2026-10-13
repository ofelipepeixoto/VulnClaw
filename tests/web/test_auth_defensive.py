# Copyright (c) 2026 Carlos Felipe. SPDX-License-Identifier: MIT
"""Offline regressions for malformed credentials and configured token storage."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from vulnclaw.web import auth


@pytest.fixture
def token_file(monkeypatch, tmp_path):
    directory = tmp_path / "config"
    monkeypatch.setattr(auth, "TOKEN_DIR", directory)
    monkeypatch.setattr(auth, "TOKEN_FILE", directory / "web_token")
    directory.mkdir()
    return directory / "web_token"


@pytest.mark.parametrize("token", [None, 1, b"test", "", "é", "x" * 4097])
def test_invalid_presented_token_is_rejected(token_file, token):
    token_file.write_text("fixture-token", encoding="utf-8")
    assert auth.verify_token(token) is False


@pytest.mark.parametrize("stored", [b"", b" \n", "é".encode(), b"\xff", b"x" * 4097])
def test_invalid_stored_token_is_rejected(token_file, stored):
    token_file.write_bytes(stored)
    assert auth.verify_token(stored.decode("utf-8", errors="replace").strip()) is False


def test_verification_does_not_create_directory(token_file):
    token_file.parent.rmdir()
    assert auth.verify_token("fixture-token") is False
    assert not token_file.parent.exists()


def test_unreadable_token_fails_closed(token_file, monkeypatch):
    token_file.mkdir()
    assert auth.verify_token("fixture-token") is False


def test_configured_directory_is_used(tmp_path):
    expected = tmp_path / "configured"
    env = {**os.environ, "VULNCLAW_CONFIG_DIR": str(expected)}
    result = subprocess.run(
        [sys.executable, "-c", "from vulnclaw.web.auth import TOKEN_FILE; print(TOKEN_FILE)"],
        env=env, check=True, capture_output=True, text=True,
    )
    assert Path(result.stdout.strip()) == expected / "web_token"


@pytest.mark.asyncio
async def test_empty_bearer_cannot_authenticate_empty_file(token_file):
    token_file.write_text("", encoding="utf-8")

    async def protected(request):
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/api/private", protected)])
    app.add_middleware(auth.AuthMiddleware)
    transport = httpx.ASGITransport(app=app, client=("192.0.2.1", 1234))
    async with httpx.AsyncClient(transport=transport, base_url="http://test.invalid") as client:
        response = await client.get("/api/private", headers={"Authorization": "Bearer "})
    assert response.status_code == 403
