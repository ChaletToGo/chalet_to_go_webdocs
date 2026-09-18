from pathlib import Path
from urllib.parse import quote
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ..site.routes import whatsapp
from ..shared.urls import local_url

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')
ASSETS = Path(__file__).parent.parent / '3d' / 'chalé_basico'

@router.get('/experiencia-3d', include_in_schema=False)
async def showroom(request: Request):
    def asset(name):
        if not (ASSETS / name).is_file():
            return ''
        return local_url(request.url_for('models', path=quote('chalé_basico/' + name)))
    models = [{'id': key, 'label': label, 'url': asset(filename)} for key, label, filename in [
        ('exterior', 'Exterior', 'basico_exterior_modelagem.glb'),
        ('structure', 'Estrutura', 'basico_estrutura_modelagem.glb'),
    ]]
    gallery = [{'url': asset(name), 'title': title, 'description': description} for name, title, description in [
        ('interior_basico.jpg', 'Acolhimento em cada detalhe', 'Madeira natural, luz e texturas para viver perto do essencial.'),
        ('interior_basico2.jpg', 'Espaço para desacelerar', 'A sala recebe a luz natural e conecta a entrada ao restante do chalé.'),
        ('interior_basico3.jpg', 'Um refúgio no mezanino', 'O espaço de descanso ocupa o nível superior.'),
        ('interior_basico4.jpg', 'Conforto na medida', 'Soluções compactas para a rotina dentro do chalé.'),
    ] if (ASSETS / name).is_file()]
    response = templates.TemplateResponse(request, 'product.html', {
        'model_url': models[0]['url'], 'models': models, 'gallery': gallery,
        'plan_url': asset('planta_chale_basico.jpg'),
        'contact_url': whatsapp('Olá! Explorei o Chalé Básico em 3D e gostaria de conversar sobre esse projeto.'),
    })
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response
