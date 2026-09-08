import csv
import io
import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from filelock import FileLock
from pydantic import BaseModel, Field, field_validator
from tinydb import TinyDB, Query
from tinydb.storages import Storage

import json

router = APIRouter()
security = HTTPBasic(auto_error=False)
templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')
HEADERS = {'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow', 'Referrer-Policy': 'no-referrer'}


def admin(request: Request, credentials: HTTPBasicCredentials | None = Depends(security)):
    username, password = os.getenv('ADMIN_USERNAME', ''), os.getenv('ADMIN_PASSWORD', '')
    if not username or not password:
        raise HTTPException(503, 'Configure ADMIN_USERNAME e ADMIN_PASSWORD para habilitar o painel.')
    if not credentials or not (secrets.compare_digest(credentials.username.encode(), username.encode()) & secrets.compare_digest(credentials.password.encode(), password.encode())):
        raise HTTPException(401, 'Autenticação necessária.', headers={'WWW-Authenticate': 'Basic realm="Chalet to Go Admin", charset="UTF-8"'})
    if request.method not in ('GET', 'HEAD') and request.headers.get('x-admin-request') != '1':
        raise HTTPException(403, 'Requisição não autorizada.')


class AtomicStorage(Storage):
    """Atomic replacement; all readers/writers also hold the same process-safe lock."""
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        return json.loads(self.path.read_text('utf-8')) if self.path.exists() else None

    def write(self, data):
        temporary = self.path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)


@contextmanager
def database():
    path = Path(os.getenv('ADMIN_DB_PATH', 'data/admin.json')).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + '.lock', timeout=15):
        with TinyDB(path, storage=AtomicStorage) as db:
            yield db.table('qrcodes')


def now():
    return datetime.now(timezone.utc).isoformat()


def valid_url(value):
    parsed = urlsplit(value)
    if parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or parsed.password or any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError('Informe uma URL HTTP ou HTTPS válida, sem credenciais ou espaços.')
    try:
        parsed.port
    except ValueError:
        raise ValueError('Porta inválida.')
    if parsed.path.rstrip('/').startswith('/q/'):
        raise ValueError('Use o destino final, não outro link de QR Code.')
    return value


class QRInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=2048)
    campaign: str = Field(default='', max_length=100)
    active: bool = True
    color: str = '#0E2A20'
    expires_at: datetime | None = None

    @field_validator('name', 'campaign', 'destination', mode='before')
    @classmethod
    def strip(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator('destination')
    @classmethod
    def url(cls, value):
        return valid_url(value)

    @field_validator('color')
    @classmethod
    def palette(cls, value):
        if value not in ('#0E2A20', '#556B4E', '#8B5E34', '#000000'):
            raise ValueError('Selecione uma cor da paleta.')
        return value

    @field_validator('expires_at')
    @classmethod
    def aware(cls, value):
        if value and value.tzinfo is None:
            raise ValueError('Informe o fuso horário da expiração.')
        return value


def find(table, code):
    row = table.get(Query().code == code)
    if row is None:
        raise HTTPException(404, 'QR Code não encontrado.')
    return row


def output(row):
    result = dict(row)
    result['status'] = 'paused' if not row['active'] else 'expired' if row['expires_at'] and datetime.fromisoformat(row['expires_at']) <= datetime.now(timezone.utc) else 'active'
    return result


@router.get('/admin', response_class=HTMLResponse, dependencies=[Depends(admin)])
@router.get('/admin/qrcodes', response_class=HTMLResponse, dependencies=[Depends(admin)])
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name='qrcodes.html', context={}, headers=HEADERS)


@router.get('/admin/api/qrcodes', dependencies=[Depends(admin)])
def listing():
    with database() as table:
        rows = [output(row) for row in table.all()]
    return Response(json.dumps(rows), media_type='application/json', headers=HEADERS)


@router.post('/admin/api/qrcodes', status_code=201, dependencies=[Depends(admin)])
def create(payload: QRInput):
    base = os.getenv('QR_BASE_URL') or os.getenv('SITE_URL', 'http://localhost:8000')
    try:
        valid_url(base)
    except ValueError:
        raise HTTPException(503, 'Configure QR_BASE_URL com o endereço público do site.')
    with database() as table:
        code = secrets.token_urlsafe(9)
        while table.contains(Query().code == code):
            code = secrets.token_urlsafe(9)
        row = {**payload.model_dump(mode='json'), 'code': code, 'url': base.rstrip('/') + '/q/' + code, 'created_at': now(), 'updated_at': now(), 'total': 0, 'last_access': None, 'daily': {}}
        table.insert(row)
    return output(row)


@router.put('/admin/api/qrcodes/{code}', dependencies=[Depends(admin)])
def update(code: str, payload: QRInput):
    with database() as table:
        row = find(table, code)
        changes = {**payload.model_dump(mode='json'), 'updated_at': now()}
        table.update(changes, doc_ids=[row.doc_id])
        return output({**row, **changes})


@router.get('/admin/api/export.csv', dependencies=[Depends(admin)])
def export():
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(['Nome', 'Campanha', 'Destino', 'Link QR', 'Status', 'Acessos', 'Criado em', 'Último acesso'])
    with database() as table:
        for row in table.all():
            cells = [row['name'], row['campaign'], row['destination'], row['url'], output(row)['status'], row['total'], row['created_at'], row['last_access'] or '']
            writer.writerow(["'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v for v in cells])
    return Response('\ufeff' + stream.getvalue(), media_type='text/csv; charset=utf-8', headers={**HEADERS, 'Content-Disposition': 'attachment; filename="chalet-qrcodes.csv"'})


@router.get('/admin/api/qrcodes/{code}/download', dependencies=[Depends(admin)])
def download(code: str, format: str = 'png'):
    if format not in ('png', 'svg'):
        raise HTTPException(422, 'Formato deve ser png ou svg.')
    with database() as table:
        row = find(table, code)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=16, border=4)
    qr.add_data(row['url'])
    qr.make(fit=True)
    # Keep the quiet zone and modules intact; place branding outside the code.
    if format == 'png':
        from PIL import Image, ImageDraw
        img = qr.make_image(fill_color=row['color'], back_color='white').convert('RGB')
        canvas = Image.new('RGB', (img.width, img.height + 64), 'white')
        canvas.paste(img, (0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text((img.width / 2, img.height + 16), 'CHALET TO GO', fill=row['color'], anchor='mt', font_size=24)
        buffer = io.BytesIO()
        canvas.save(buffer, format='PNG')
        content = buffer.getvalue()
    else:
        matrix = qr.get_matrix()
        size = len(matrix)
        paths = ' '.join(f'M{x},{y}h1v1h-1z' for y, line in enumerate(matrix) for x, black in enumerate(line) if black)
        content = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size*16}" height="{(size+4)*16}" viewBox="0 0 {size} {size+4}"><rect width="100%" height="100%" fill="white"/><path d="{paths}" fill="{row["color"]}"/><text x="{size/2}" y="{size+2}" text-anchor="middle" font-family="Arial,sans-serif" font-size="1.5" fill="{row["color"]}">CHALET TO GO</text></svg>'
    return Response(content, media_type='image/png' if format == 'png' else 'image/svg+xml', headers={**HEADERS, 'Content-Disposition': f'attachment; filename="chalet-{code}.{format}"'})


@router.get('/q/{code}')
def redirect(code: str):
    with database() as table:
        row = find(table, code)
        if output(row)['status'] != 'active':
            return HTMLResponse('<html lang="pt-BR"><meta name="viewport" content="width=device-width"><title>Chalet to Go</title><body><h1>Chalet to Go</h1><p>Este QR Code está temporariamente indisponível.</p></body></html>', status_code=410, headers=HEADERS)
        timestamp = now()
        daily = row['daily'].copy()
        day = timestamp[:10]
        daily[day] = daily.get(day, 0) + 1
        table.update({'total': row['total'] + 1, 'last_access': timestamp, 'daily': daily}, doc_ids=[row.doc_id])
    return RedirectResponse(row['destination'], status_code=302, headers=HEADERS)
