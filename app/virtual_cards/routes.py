import json
import logging
import re
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from ..shared.urls import local_url

CARD_DIR = Path(__file__).resolve().parent
router = APIRouter(prefix='/card', tags=['Cards'])
templates = Jinja2Templates(directory=CARD_DIR / 'templates')
templates.env.filters['local_url'] = local_url
logger = logging.getLogger(__name__)


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

    @field_validator('*')
    @classmethod
    def clean_text(cls, value):
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
    actions = []
    if card.whatsapp:
        actions.append(('WhatsApp', 'Vamos conversar', 'https://wa.me/' + re.sub(r'\D', '', card.whatsapp), 'chat'))
    if card.telefone:
        actions.append(('Telefone', card.telefone, 'tel:+' + re.sub(r'\D', '', card.telefone), 'phone'))
    if card.email:
        actions.append(('E-mail', card.email, 'mailto:' + card.email, 'mail'))
    for field, label, subtitle in [('site', 'Conheça a Chalet to Go', 'Nosso site'), ('instagram', 'Instagram', 'Acompanhe nossas histórias'), ('linkedin', 'LinkedIn', 'Vamos nos conectar')]:
        if value := getattr(card, field):
            actions.append((label, subtitle, value, 'arrow'))
    return templates.TemplateResponse(request, 'card.html', {'card': card, 'slug': slug, 'actions': actions}, headers={'Cache-Control': 'no-store'})


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
def card_contact(slug: str):
    card = load_card(slug)
    lines = ['BEGIN:VCARD', 'VERSION:3.0', 'FN:' + vcard_escape(card.nome), 'N:;' + vcard_escape(card.nome) + ';;;', 'ORG:' + vcard_escape(card.empresa), 'TITLE:' + vcard_escape(card.cargo)]
    for field, key in [('telefone', 'TEL;TYPE=WORK,VOICE'), ('email', 'EMAIL;TYPE=WORK'), ('site', 'URL'), ('sobre', 'NOTE')]:
        if value := getattr(card, field):
            lines.append(key + ':' + vcard_escape(value))
    if card.whatsapp and not card.telefone:
        lines.append('TEL;TYPE=CELL:+' + re.sub(r'\D', '', card.whatsapp))
    lines.append('END:VCARD')
    return Response('\r\n'.join(map(fold_line, lines)) + '\r\n', media_type='text/vcard; charset=utf-8', headers={'Content-Disposition': f'attachment; filename="{slug}.vcf"', 'Cache-Control': 'no-store'})
