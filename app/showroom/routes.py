from pathlib import Path
from urllib.parse import quote
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ..shared.urls import local_url
from .cache import file_version

router = APIRouter()
ASSETS = Path(__file__).parent.parent / '3d' / 'chalé_basico'

@router.get('/experiencia-3d', include_in_schema=False)
async def showroom(request: Request):
    query = '?' + request.url.query if request.url.query else ''
    return RedirectResponse('/chales/basic' + query, status_code=301)

def product_media(request: Request):
    def asset(name):
        if not (ASSETS / name).is_file():
            return ''
        return local_url(request.url_for('models', path=quote('chalé_basico/' + name))) + '?v=' + file_version((ASSETS / name).stat())
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
    return {'hero_url': '/static/images/plano_basic.png', 'model_url': models[0]['url'],
            'models': models, 'interior_photos': gallery, 'plan_url': asset('planta_chale_basico.jpg')}
