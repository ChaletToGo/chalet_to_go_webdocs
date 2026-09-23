"""Country derived from the visitor IP by the controlled Cloudflare proxy.

Never infer commercial location from language, cookies or query parameters.
"""
import os
from ipaddress import ip_address


def country_from_ip(request):
    # Explicit local preview only: never infer prices from the selected language.
    preview = os.getenv('LOCAL_PREVIEW_COUNTRY', '').strip().upper()
    peer = request.client.host if request.client else ''
    try:
        loopback = ip_address(peer).is_loopback
    except ValueError:
        loopback = False
    if (request.url.hostname in ('localhost', '127.0.0.1', '::1') and loopback
            and len(preview) == 2 and preview.isascii() and preview.isalpha() and preview != 'XX'):
        return preview
    if os.getenv('TRUST_COUNTRY_HEADER', '').lower() not in ('1', 'true'):
        return ''
    country = request.headers.get('cf-ipcountry', '').strip().upper()
    if len(country) == 2 and country.isascii() and country.isalpha() and country != 'XX':
        return country
    return ''
