"""Manually configured starting prices; no automatic currency conversion."""
import json
from decimal import Decimal
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name('prices.json')
LABELS = {
    'pt-BR': ('A partir de', 'Sob consulta'),
    'pt-PT': ('A partir de', 'Sob consulta'),
    'en': ('From', 'Price on request'),
    'de': ('Ab', 'Preis auf Anfrage'),
    'fr': ('À partir de', 'Prix sur demande'),
    'it': ('A partire da', 'Prezzo su richiesta'),
    'rm': ('A partir da', 'Pretsch sin dumonda'),
}
SYMBOLS = {'BRL': 'R$', 'EUR': '€', 'CHF': 'CHF'}


def pricing_context(country):
    config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    currency = config['country_currencies'].get(country, config['default_currency'])
    if currency not in SYMBOLS:
        raise ValueError('Unsupported currency in prices.json')
    return config, currency


def plan_price(config, currency, slug, locale):
    value = config['plans'][slug][currency]
    prefix, on_request = LABELS[locale]
    if value is None:
        return {'price': None, 'currency': currency, 'price_display': f'{on_request} · {currency}'}
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Prices must be positive numbers or null in prices.json')
    amount = Decimal(str(value))
    if not amount.is_finite() or amount <= 0 or amount != amount.quantize(Decimal('0.01')):
        raise ValueError('Prices must be positive, with at most two decimal places')
    grouping = ',' if locale == 'en' else '’' if locale == 'rm' else '\u202f' if locale in ('fr', 'pt-PT') else '.'
    decimal = '.' if locale in ('en', 'rm') else ','
    whole, cents = f'{amount:,.2f}'.split('.')
    formatted = whole.replace(',', grouping) + (decimal + cents if cents != '00' else '')
    return {'price': value, 'currency': currency,
            'price_display': f'{prefix} {SYMBOLS[currency]} {formatted}'}
