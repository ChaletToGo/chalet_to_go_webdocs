"""Server-rendered magazine translations and country/language negotiation."""
import json
import os
from functools import lru_cache
from pathlib import Path
from .financials import budget_context, product_context

LOCALES = {
    'pt-BR': 'Português · Brasil', 'pt-PT': 'Português · Portugal',
    'en': 'English', 'de': 'Deutsch', 'fr': 'Français',
    'it': 'Italiano', 'rm': 'Rumantsch Grischun',
}
COUNTRIES = {'BR': 'pt-BR', 'CH': 'en', 'IT': 'it', 'FR': 'fr', 'DE': 'de', 'PT': 'pt-PT'}
SWISS_LOCALES = ('en', 'rm', 'de', 'it', 'fr')
CATALOG_DIR = Path(__file__).parent / 'locales'


@lru_cache(maxsize=7)
def catalog(locale):
    with (CATALOG_DIR / f'{locale}.json').open(encoding='utf-8') as file:
        return json.load(file)


def normalize_locale(value):
    return next((locale for locale in LOCALES if locale.lower() == (value or '').lower()), None)


def browser_locale(header):
    preferences = []
    for order, item in enumerate(header.split(',')):
        parts = item.strip().split(';')
        tag = parts[0].strip().replace('_', '-').lower()
        try:
            quality = next((float(p.strip()[2:]) for p in parts[1:] if p.strip().startswith('q=')), 1.0)
        except ValueError:
            continue
        if not 0 < quality <= 1:
            continue
        preferences.append((-quality, order, tag))
    for _, _, tag in sorted(preferences):
        # A regional browser preference is a fallback, not a country measurement.
        if tag.endswith('-ch'):
            return 'en'
        exact = normalize_locale(tag)
        if exact:
            return exact
        language = tag.split('-')[0]
        if language == 'pt':
            return 'pt-BR'
        if language in LOCALES:
            return language
    return 'en'


def resolve_locale(request):
    explicit = normalize_locale(request.query_params.get('lang'))
    saved = None if request.query_params.get('lang') == 'auto' else normalize_locale(request.cookies.get('chalet-language'))
    # Enable only behind the controlled proxy, which must overwrite this header.
    # Country is used for presentation only, never for authentication/authorization.
    country = ''
    if os.getenv('TRUST_COUNTRY_HEADER', '').lower() in ('1', 'true'):
        candidate = request.headers.get('cf-ipcountry', '').upper()
        if len(candidate) == 2 and candidate.isascii() and candidate.isalpha() and candidate not in ('XX', 'T1'):
            country = candidate
    if explicit:
        return explicit, country, 'explicit'
    if saved:
        return saved, country, 'saved'
    if country:
        return COUNTRIES.get(country, 'en'), country, 'country'
    return browser_locale(request.headers.get('accept-language', '')), country, 'browser'


def context_for(request):
    locale, country, source = resolve_locale(request)
    data = catalog(locale)
    options = list(SWISS_LOCALES) + ['pt-BR', 'pt-PT'] if country == 'CH' else list(LOCALES)
    return {
        'pages': data['pages'], 'ui': data['ui'], 'locale': locale,
        'country': country, 'locale_source': source,
        'language_options': [(code, LOCALES[code]) for code in options],
        'budget': budget_context(),
        'products': product_context(), 'finance':data['finance'],
    }
