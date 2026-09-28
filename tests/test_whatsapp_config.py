import json
import re
from html import unescape
from urllib.parse import urlsplit

import pytest

from app.shared.contact import whatsapp_number
from test_i18n import get


@pytest.mark.parametrize('number', ['5511999990000', '41791234567'])
def test_every_home_whatsapp_link_uses_environment(monkeypatch, number):
    monkeypatch.setenv('WHATSAPP_NUMBER', number)
    status, _, html = get({'lang': 'pt-BR'}, path='/')
    assert status == 200
    links = [unescape(link) for link in re.findall(r'href="([^"]+)"', html)
             if link.startswith('https://wa.me/')]
    assert len(links) == 8  # Menu, hero, timber, three models, warranty, footer.
    assert all(urlsplit(link).path == '/' + number for link in links)
    schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html).group(1))
    organization = next(item for item in schema['@graph'] if item['@type'] == 'Organization')
    assert organization['contactPoint']['telephone'] == '+' + number


def test_missing_number_has_no_hardcoded_fallback(monkeypatch):
    monkeypatch.delenv('WHATSAPP_NUMBER')
    with pytest.raises(ValueError, match='WHATSAPP_NUMBER'):
        whatsapp_number()


@pytest.mark.parametrize('country,number', [
    ('BR', '5531984748754'), ('CH', '41791914638'), ('DE', '41791914638'),
    ('IT', '41791914638'), ('PT', '41791914638'), ('FR', '41791914638'),
    ('US', '5531984748754'), ('XX', '5531984748754'), ('', '5531984748754'),
])
def test_country_contacts_independent_of_language(country, number):
    for path in ['/', '/chales/basic', '/contato', '/experiencia-3d', '/eco-villa-natal']:
        status, headers, html = get({'lang': 'en'}, path=path, trusted=True,
            headers={'cf-ipcountry': country, 'cookie': 'chalet-language=fr'})
        assert status == 200
        links = re.findall(r'href="https://wa.me/([0-9]+)[?\"]', html)
        assert links and set(links) == {number}
        assert b'no-store' in headers[b'cache-control']
        assert b'CF-IPCountry' in headers[b'vary']
        if path == '/':
            assert '"telephone": "+' + number + '"' in html


def test_untrusted_country_does_not_route_to_foreign_contact():
    _, _, html = get({'lang': 'de'}, path='/', trusted=False, headers={'cf-ipcountry': 'DE'})
    assert set(re.findall(r'href="https://wa.me/([0-9]+)[?\"]', html)) == {'5531984748754'}


def test_editing_config_changes_contact(monkeypatch, tmp_path):
    from app.shared import contact
    path = tmp_path / 'contacts.json'
    path.write_text(json.dumps({'default': {'env': 'WHATSAPP_NUMBER'},
                               'countries': {'CH': {'number': '+41 79 123 45 67'}}}), encoding='utf-8')
    monkeypatch.setattr(contact, 'CONFIG_PATH', path)
    _, _, html = get(path='/', trusted=True, headers={'cf-ipcountry': 'CH'})
    assert set(re.findall(r'href="https://wa.me/([0-9]+)[?\"]', html)) == {'41791234567'}
