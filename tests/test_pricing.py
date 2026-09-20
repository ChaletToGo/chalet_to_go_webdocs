import json
import re

import pytest

from app.site import pricing
from app.shared.i18n import LOCALES
from test_i18n import get


@pytest.mark.parametrize('country,currency,symbol', [
    ('BR', 'BRL', 'R$'), ('CH', 'CHF', 'CHF'), ('DE', 'EUR', '€'),
    ('FR', 'EUR', '€'), ('IT', 'EUR', '€'), ('PT', 'EUR', '€'),
    ('US', 'EUR', '€'), ('', 'EUR', '€'), ('XX', 'EUR', '€')])
def test_country_prices_and_starting_offer(country, currency, symbol):
    for path in ['/', '/chales/basic', '/sobre', '/perguntas-frequentes']:
        status, headers, html = get({'lang': 'pt-BR'}, path=path, trusted=True,
                                  headers={'cf-ipcountry': country})
        assert status == 200
        assert f'A partir de {symbol} 40.000' in html
        assert b'no-store' in headers[b'cache-control']
        if path == '/chales/basic':
            graph = json.loads(re.search(r'application/ld\+json">(.*?)</script>', html).group(1))['@graph']
            offer = next(item for item in graph if item['@type'] == 'Product')['offers']
            assert offer['lowPrice'] == 40000
            assert offer['priceCurrency'] == currency
            assert 'price' not in offer


def test_language_does_not_change_currency():
    for locale in LOCALES:
        _, _, html = get({'lang': locale}, path='/', trusted=True, headers={'cf-ipcountry': 'BR'})
        assert pricing.LABELS[locale][0] + ' R$ ' in html
    _, _, html = get({'lang': 'pt-BR'}, path='/', trusted=False, headers={'cf-ipcountry': 'BR'})
    assert 'A partir de € 40.000' in html


def test_configurable_values_and_cents(monkeypatch, tmp_path):
    config = json.loads(pricing.CONFIG_PATH.read_text('utf-8'))
    config['plans']['basic']['BRL'] = 123456.78
    config['plans']['basic']['EUR'] = None
    path = tmp_path / 'prices.json'
    path.write_text(json.dumps(config), encoding='utf-8')
    monkeypatch.setattr(pricing, 'CONFIG_PATH', path)
    assert 'A partir de R$ 123.456,78' in get({'lang': 'pt-BR'}, path='/', trusted=True, headers={'cf-ipcountry': 'BR'})[2]
    html = get({'lang': 'pt-BR'}, path='/chales/basic')[2]
    assert 'Sob consulta · EUR' in html
    graph = json.loads(re.search(r'application/ld\+json">(.*?)</script>', html).group(1))['@graph']
    assert 'offers' not in next(item for item in graph if item['@type'] == 'Product')
