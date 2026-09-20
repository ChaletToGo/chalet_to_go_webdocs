"""Commercial contacts by trusted visitor country, independent of language."""
import json
import os
import re
from pathlib import Path

from .i18n import resolve_locale

CONFIG_PATH = Path(__file__).with_name('contact_numbers.json')


def whatsapp_number(request=None):
    config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    country = resolve_locale(request)[1] if request is not None else ''
    entry = config['countries'].get(country, config['default'])
    value = os.getenv(entry['env'], '') if 'env' in entry else entry['number']
    if not isinstance(value, str) or not re.fullmatch(r'\+?[0-9 ()-]+', value.strip()):
        raise ValueError('Configure um telefone válido em contact_numbers.json ou WHATSAPP_NUMBER no .env.')
    number = re.sub(r'\D', '', value)
    if not re.fullmatch(r'[1-9][0-9]{7,14}', number):
        raise ValueError('Configure o código do país em contact_numbers.json ou WHATSAPP_NUMBER no .env.')
    return number
