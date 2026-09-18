"""Portuguese sales campaign for the planned Eco Villa in Natal."""
import os
import re
from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')


@router.get('/eco-villa-natal', response_class=HTMLResponse, name='eco_villa')
async def landing(request: Request):
    number = os.getenv('ECO_VILLA_WHATSAPP_NUMBER', os.getenv('WHATSAPP_NUMBER', '5538998840910')).strip().lstrip('+')
    if not re.fullmatch(r'[1-9][0-9]{7,14}', number):
        raise ValueError('ECO_VILLA_WHATSAPP_NUMBER must contain country code and digits only')
    message = 'Olá! Tenho interesse em uma unidade Basic da Eco Villa em Natal. Gostaria de receber a apresentação, os valores e as condições de compra.'
    response = templates.TemplateResponse(request, 'index.html', {
        'whatsapp': 'https://wa.me/' + number + '?' + urlencode({'text': message}),
    })
    response.headers['Content-Language'] = 'pt-BR'
    return response
