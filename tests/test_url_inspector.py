import http.client
import socket
import urllib.request

import pytest

from app.services.url_inspector import extract_urls, inspect_url


def test_extract_urls_removes_sentence_punctuation() -> None:
    assert extract_urls("Review https://example.com/path.") == ["https://example.com/path"]


def test_malformed_url_returns_safe_error() -> None:
    result = inspect_url("not-a-url")

    assert result.valid is False
    assert result.error is not None


def test_punycode_host_is_explained_cautiously() -> None:
    result = inspect_url("https://xn--example-9ta.test")

    assert result.valid is True
    assert any(signal.signal_id == "punycode_host" for signal in result.signals)


def test_shortener_is_a_cautious_structural_signal() -> None:
    result = inspect_url("https://bit.ly/example")

    assert result.valid is True
    assert any(signal.signal_id == "url_shortener" for signal in result.signals)


def test_embedded_credentials_are_visible_without_revealing_a_destination_claim() -> None:
    result = inspect_url("https://login:secret@bank.example.attacker.test/sign-in")

    assert result.valid is True
    assert result.host == "bank.example.attacker.test"
    assert {signal.signal_id for signal in result.signals} >= {"embedded_url_credentials", "deep_subdomain_structure"}


def test_https_does_not_suppress_structural_warnings() -> None:
    result = inspect_url("https://xn--example-9ta.login.example.attacker.test/%2Fsignin")

    assert result.scheme == "https"
    assert {signal.signal_id for signal in result.signals} >= {
        "punycode_host",
        "deep_subdomain_structure",
        "encoded_url_component",
    }


def test_url_inspection_does_not_use_network_or_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("URL inspection must not perform network I/O")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden_network)
    monkeypatch.setattr(socket, "create_connection", forbidden_network)
    monkeypatch.setattr(http.client, "HTTPConnection", forbidden_network)
    monkeypatch.setattr(http.client, "HTTPSConnection", forbidden_network)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden_network)

    result = inspect_url("https://198.51.100.7/login?next=%2Faccount")

    assert result.valid is True
    assert any(signal.signal_id == "ip_address_host" for signal in result.signals)
