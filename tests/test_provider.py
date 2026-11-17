"""Provider contract tests use HTTP mocks; no real model or credential is contacted."""

import asyncio
from dataclasses import replace
import httpx
import pytest
from pydantic import ValidationError
from backend.agents.provider import Provider


def provider_with_transport(env, monkeypatch, handler):
    original = httpx.AsyncClient
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    settings = replace(
        env.settings,
        mode="hosted",
        model_url="https://model.example.test/v1/chat/completions",
        model_name="mock-model",
        model_key="test-only-no-real-key",
    )
    return Provider(settings)


def test_hosted_adapter_validates_structured_intents(env, monkeypatch):
    def respond(request):
        assert request.headers["Authorization"] == "Bearer test-only-no-real-key"
        return httpx.Response(
            200, json={"choices": [{"message": {"content": '{"support":true,"sales":true}'}}]}
        )

    provider = provider_with_transport(env, monkeypatch, respond)
    result = asyncio.run(provider.intake("A test message"))
    assert result.support and result.sales


def test_hosted_adapter_retries_transient_error_only(env, monkeypatch):
    calls = []

    def respond(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"support":true}'}}]})

    provider = provider_with_transport(env, monkeypatch, respond)
    assert asyncio.run(provider.intake("A test message")).support
    assert len(calls) == 2


def test_invalid_model_fields_fail_instead_of_granting_write_authority(env, monkeypatch):
    provider = provider_with_transport(
        env,
        monkeypatch,
        lambda request: httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"support":true,"execute_sql":"DELETE FROM users"}'}}]
            },
        ),
    )
    with pytest.raises(ValidationError):
        asyncio.run(provider.intake("A test message"))
