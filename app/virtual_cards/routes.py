import json
import logging
import re
from pathlib import Path
from urllib.parse import urlsplit, urlencode, quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from ..shared.urls import local_url
from ..shared.i18n import LOCALES, language_context, apply_language_headers
from .i18n import CATALOGS

CARD_DIR = Path(__file__).resolve().parent
router = APIRouter(prefix='/card', tags=['Cards'])
templates = Jinja2Templates(directory=CARD_DIR / 'templates')
templates.env.filters['local_url'] = local_url
logger = logging.getLogger(__name__)


class CardTranslation(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    cargo: str = ''
    sobre: str = ''

    @field_validator('*')
    @classmethod
    def clean_text(cls, value):
        if len(value) > 2000 or any(ord(char) < 32 for char in value):
            raise ValueError('Texto inválido')
        return value


class Card(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    nome: str
    cargo: str
    empresa: str = 'Chalet to Go'
    telefone: str = ''
    whatsapp: str = ''
    email: str = ''
    site: str = ''
    instagram: str = ''
    linkedin: str = ''
    localizacao: str = ''
    sobre: str = ''
    traducoes: dict[str, CardTranslation] = Field(default_factory=dict)
    foto: str = ''

    @field_validator('traducoes')
    @classmethod
    def supported_translations(cls, value):
        if any(locale not in LOCALES for locale in value):
            raise ValueError('Idioma não suportado')
        return value

    @field_validator('*')
    @classmethod
    def clean_text(cls, value):
        if not isinstance(value, str):
            return value
        if len(value) > 2000 or any(ord(char) < 32 for char in value):
            raise ValueError('Use texto sem caracteres de controle, com até 2000 caracteres')
        return value

    @field_validator('nome', 'cargo', 'empresa')
    @classmethod
    def required_text(cls, value):
        if not value:
            raise ValueError('Campo obrigatório')
        return value

    @field_validator('site', 'instagram', 'linkedin')
    @classmethod
    def safe_link(cls, value):
        if value:
            parsed = urlsplit(value)
            if parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or any(c.isspace() for c in value):
                raise ValueError('Use uma URL completa https://')
        return value

    @field_validator('telefone', 'whatsapp')
    @classmethod
    def phone_number(cls, value):
        if value and (not re.fullmatch(r'\+?[0-9 ()-]+', value) or not 8 <= len(re.sub(r'\D', '', value)) <= 15):
            raise ValueError('Use telefone com código do país e 8 a 15 dígitos')
        return value

    @field_validator('email')
    @classmethod
    def email_address(cls, value):
        if value and not re.fullmatch(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', value):
            raise ValueError('E-mail inválido')
        return value


def card_photo_url(value: str) -> str | None:
    """Resolve optional photos only inside the cards' public static directory."""
    if not value:
        return None
    value = value.replace('\\', '/')
    for prefix in ('/static/cards/', 'app/virtual_cards/static/', 'static/'):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    root = (CARD_DIR / 'static').resolve()
    try:
        path = (root / value).resolve()
        if not path.is_relative_to(root) or path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'} or not path.is_file():
            return None
        return '/static/cards/' + quote(path.relative_to(root).as_posix(), safe='/')
    except (OSError, ValueError):
        return None


def load_card(slug: str) -> Card:
    if not re.fullmatch(r'[a-z0-9]+(?:[_-][a-z0-9]+)*', slug) or len(slug) > 100:
        raise HTTPException(404, 'Cartão não encontrado')
    path = (CARD_DIR / f'{slug}.json').resolve()
    if path.parent != CARD_DIR.resolve() or not path.is_file():
        raise HTTPException(404, 'Cartão não encontrado')
    try:
        return Card.model_validate(json.loads(path.read_text(encoding='utf-8-sig')))
    except (OSError, ValueError, ValidationError):
        logger.exception('Não foi possível carregar o cartão %s', slug)
        raise HTTPException(500, 'Cartão temporariamente indisponível') from None


@router.get('/{slug}', response_class=HTMLResponse, name='virtual_card')
def card_page(request: Request, slug: str):
    card = load_card(slug)
    context = language_context(request)
    t = CATALOGS[context['locale']]
    if translation := card.traducoes.get(context['locale']):
        card = card.model_copy(update={key: value for key, value in translation.model_dump().items() if value})
    actions = []
    if card.whatsapp:
        actions.append(('WhatsApp', t['connect'], 'https://wa.me/' + re.sub(r'\D', '', card.whatsapp), 'chat'))
    if card.telefone:
        actions.append((t['phone'], card.telefone, 'tel:+' + re.sub(r'\D', '', card.telefone), 'phone'))
    if card.email:
        actions.append((t['email'], card.email, 'mailto:' + card.email, 'mail'))
    if card.localizacao:
        actions.append((t['maps'], card.localizacao, 'https://www.google.com/maps/search/?' + urlencode({'api': '1', 'query': card.localizacao}), 'map'))
    for field, label, subtitle in [('site', t['site'], t['site_sub']), ('instagram', 'Instagram', t['instagram_sub']), ('linkedin', 'LinkedIn', t['linkedin_sub'])]:
        if value := getattr(card, field):
            actions.append((label, subtitle, value, 'arrow'))
    response = templates.TemplateResponse(request, 'card.html', {**context, 't': t, 'card': card, 'slug': slug, 'actions': actions, 'photo_url': card_photo_url(card.foto)})
    return apply_language_headers(response, request, context)


def vcard_escape(value: str) -> str:
    return value.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def fold_line(line: str) -> str:
    chunks, current = [], ''
    for char in line:
        if len((current + char).encode('utf-8')) > 75:
            chunks.append(current)
            current = ' '
        current += char
    return '\r\n'.join([*chunks, current])


@router.get('/{slug}/contact.vcf', name='virtual_card_contact')
def card_contact(request: Request, slug: str):
    card = load_card(slug)
    context = language_context(request)
    if translation := card.traducoes.get(context['locale']):
        card = card.model_copy(update={key: value for key, value in translation.model_dump().items() if value})
    lines = ['BEGIN:VCARD', 'VERSION:3.0', 'FN:' + vcard_escape(card.nome), 'N:;' + vcard_escape(card.nome) + ';;;', 'ORG:' + vcard_escape(card.empresa), 'TITLE:' + vcard_escape(card.cargo)]
    for field, key in [('telefone', 'TEL;TYPE=WORK,VOICE'), ('email', 'EMAIL;TYPE=WORK'), ('site', 'URL'), ('sobre', 'NOTE')]:
        if value := getattr(card, field):
            lines.append(key + ':' + vcard_escape(value))
    if card.whatsapp and not card.telefone:
        lines.append('TEL;TYPE=CELL:+' + re.sub(r'\D', '', card.whatsapp))
    if card.localizacao:
        lines.append('ADR;TYPE=WORK:;;' + vcard_escape(card.localizacao) + ';;;;')
    lines.append('END:VCARD')
    response = Response('\r\n'.join(map(fold_line, lines)) + '\r\n', media_type='text/vcard; charset=utf-8', headers={'Content-Disposition': f'attachment; filename="{slug}.vcf"'})
    return apply_language_headers(response, request, context)
