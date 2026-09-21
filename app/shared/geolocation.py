"""Country derived from the visitor IP by the controlled Cloudflare proxy.

Never infer commercial location from language, cookies or query parameters.
"""
import os


def country_from_ip(request):
    if os.getenv('TRUST_COUNTRY_HEADER', '').lower() not in ('1', 'true'):
        return ''
    country = request.headers.get('cf-ipcountry', '').strip().upper()
    if len(country) == 2 and country.isascii() and country.isalpha() and country != 'XX':
        return country
    return ''
