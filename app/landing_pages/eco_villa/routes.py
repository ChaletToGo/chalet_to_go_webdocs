"""Portuguese sales campaign for the planned Eco Villa in Natal."""
from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.shared.contact import whatsapp_number

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')


@router.get('/eco-villa-natal', response_class=HTMLResponse, name='eco_villa')
async def landing(request: Request):
    number = whatsapp_number(request)
    message = 'Olá! Tenho interesse em uma unidade Basic da Eco Villa em Natal. Gostaria de receber a apresentação, os valores e as condições de compra.'
    response = templates.TemplateResponse(request, 'index.html', {
        'whatsapp': 'https://wa.me/' + number + '?' + urlencode({'text': message}),
    })
    response.headers['Content-Language'] = 'pt-BR'
    response.headers['Cache-Control'] = 'private, no-store'
    response.headers['Vary'] = 'CF-IPCountry'
    return response
