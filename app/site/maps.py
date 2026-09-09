"""Optional, explicitly configured public business location."""
import os
from urllib.parse import urlencode

LABELS = {
    'pt-BR': ('Localização', 'Encontre a Chalet To GO', 'Abrir no Google Maps'),
    'pt-PT': ('Localização', 'Encontre a Chalet To GO', 'Abrir no Google Maps'),
    'en': ('Location', 'Find Chalet To GO', 'Open in Google Maps'),
    'fr': ('Localisation', 'Retrouvez Chalet To GO', 'Ouvrir dans Google Maps'),
    'de': ('Standort', 'Chalet To GO finden', 'In Google Maps öffnen'),
    'it': ('Dove siamo', 'Trova Chalet To GO', 'Apri in Google Maps'),
    'rm': ('Lieu', 'Chattar Chalet To GO', 'Avrir en Google Maps'),
}


def map_context(locale):
    address = os.getenv('GOOGLE_MAPS_ADDRESS', 'Rte de Porrentruy 8, 2800 Delémont, Switzerland').strip()
    key = os.getenv('GOOGLE_MAPS_API_KEY', '').strip()
    if not address or not key:
        return None
    language = {'pt-PT': 'pt', 'rm': 'en'}.get(locale, locale)
    return {
        'labels': LABELS[locale],
        'address': address,
        'src': 'https://www.google.com/maps/embed/v1/place?' + urlencode({
            'key': key, 'q': address, 'language': language,
        }),
        'link': 'https://www.google.com/maps/search/?' + urlencode({
            'api': '1', 'query': address,
        }),
    }
