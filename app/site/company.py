"""Confirmed public company identity, shared only within the institutional site."""
import os
from urllib.parse import urlsplit

NAME = 'Chalet To GO'
ADDRESS = {'@type': 'PostalAddress', 'streetAddress': 'Rte de Porrentruy 8',
           'postalCode': '2800', 'addressLocality': 'Delémont', 'addressCountry': 'CH'}
COUNTRIES = {'pt-BR': 'Suíça', 'pt-PT': 'Suíça', 'en': 'Switzerland',
             'fr': 'Suisse', 'de': 'Schweiz', 'it': 'Svizzera', 'rm': 'Svizra'}
LABELS = {'pt-BR': ('Endereço da empresa', 'Perfis oficiais'),
          'pt-PT': ('Endereço da empresa', 'Perfis oficiais'),
          'en': ('Company address', 'Official profiles'),
          'fr': ('Adresse de l’entreprise', 'Profils officiels'),
          'de': ('Firmenadresse', 'Offizielle Profile'),
          'it': ('Indirizzo dell’azienda', 'Profili ufficiali'),
          'rm': ('Adressa da l’interpresa', 'Profils uffizials')}


def profiles():
    """Only URLs explicitly supplied by the operator, never guessed social handles."""
    result = []
    for value in os.getenv('SITE_OFFICIAL_PROFILES', '').split(','):
        value = value.strip()
        try:
            parsed = urlsplit(value)
            valid = parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
        except ValueError:
            valid = False
        if valid and value not in [item['url'] for item in result]:
            result.append({'url': value, 'label': parsed.hostname.removeprefix('www.')})
    return result


def company_context(locale):
    return {'name': NAME, 'address': 'Rte de Porrentruy 8, 2800 Delémont, ' + COUNTRIES[locale],
            'labels': LABELS[locale], 'profiles': profiles()}
