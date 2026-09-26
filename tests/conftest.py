import pytest


@pytest.fixture(autouse=True)
def commercial_contact(monkeypatch):
    """Tests must not depend on a developer's private .env file."""
    monkeypatch.setenv('WHATSAPP_NUMBER', '5531984748754')
