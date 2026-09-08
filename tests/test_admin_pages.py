import asyncio
import base64
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.main import app
from app.admin_pages.routes import QRInput, create, redirect, listing


@pytest.fixture(autouse=True)
def settings(monkeypatch, tmp_path):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'test-password')
    monkeypatch.setenv('ADMIN_DB_PATH', str(tmp_path / 'admin.json'))
    monkeypatch.setenv('QR_BASE_URL', 'https://chalet.example')


def request(path, method='GET', data=None, auth=True, csrf=True):
    messages = []
    headers = [(b'content-type', b'application/json')]
    if auth:
        headers.append((b'authorization', b'Basic ' + base64.b64encode(b'admin:test-password')))
    if csrf:
        headers.append((b'x-admin-request', b'1'))
    scope = {'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':method,'scheme':'https','path':path.split('?')[0],'raw_path':path.split('?')[0].encode(),'root_path':'','query_string':path.partition('?')[2].encode(),'headers':headers,'client':('127.0.0.1',1234),'server':('testserver',443)}
    async def receive():
        return {'type':'http.request','body':json.dumps(data).encode() if data is not None else b'','more_body':False}
    async def send(message):
        messages.append(message)
    asyncio.run(app(scope, receive, send))
    start = next(m for m in messages if m['type']=='http.response.start')
    return start['status'], dict(start['headers']), b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body')


PAYLOAD = {'name':'Recepção','destination':'https://example.com/revista','campaign':'Folder'}


def test_authentication_and_csrf(monkeypatch):
    assert request('/admin', auth=False)[0] == 401
    assert request('/admin/api/qrcodes', 'POST', PAYLOAD, csrf=False)[0] == 403
    assert request('/admin')[0] == 200
    monkeypatch.delenv('ADMIN_PASSWORD')
    assert request('/admin')[0] == 503


def test_lifecycle_and_downloads():
    status, _, body = request('/admin/api/qrcodes', 'POST', PAYLOAD)
    assert status == 201
    row = json.loads(body)
    code = row['code']
    assert row['url'] == 'https://chalet.example/q/' + code
    for fmt, signature in [('png', b'\x89PNG'), ('svg', b'<svg')]:
        status, _, body = request(f'/admin/api/qrcodes/{code}/download?format={fmt}')
        assert status == 200 and body.startswith(signature)
    assert json.loads(request('/admin/api/qrcodes')[2])[0]['total'] == 0
    status, headers, _ = request('/q/'+code, auth=False)
    assert status == 302 and headers[b'location'] == PAYLOAD['destination'].encode()
    assert headers[b'cache-control'] == b'no-store'
    changed = {**PAYLOAD, 'destination':'https://example.com/new'}
    updated = json.loads(request('/admin/api/qrcodes/'+code, 'PUT', changed)[2])
    assert updated['url'] == row['url'] and updated['total'] == 1
    assert request('/q/'+code, auth=False)[1][b'location'] == b'https://example.com/new'
    request('/admin/api/qrcodes/'+code, 'PUT', {**changed, 'active':False})
    assert request('/q/'+code, auth=False)[0] == 410
    request('/admin/api/qrcodes/'+code, 'PUT', {**changed, 'expires_at':'2000-01-01T00:00:00Z'})
    assert request('/q/'+code, auth=False)[0] == 410
    saved = json.loads(request('/admin/api/qrcodes')[2])[0]
    assert saved['total'] == 2 and sum(saved['daily'].values()) == 2
    assert request('/q/missing', auth=False)[0] == 404
    assert request(f'/admin/api/qrcodes/{code}/download', auth=False)[0] == 401


@pytest.mark.parametrize('destination', ['javascript:alert(1)', 'https://user:pass@example.com', 'https://example.com/a b', 'https://example.com/q/other', 'https://example.com:bad'])
def test_invalid_destinations(destination):
    assert request('/admin/api/qrcodes', 'POST', {**PAYLOAD,'destination':destination})[0] == 422


def test_concurrent_counts_and_csv():
    row = create(QRInput(**{**PAYLOAD,'name':'=SUM(A1)'}))
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda _: redirect(row['code']), range(32)))
    saved = json.loads(listing().body)[0]
    assert saved['total'] == 32 and sum(saved['daily'].values()) == 32
    assert "'=SUM(A1)" in request('/admin/api/export.csv')[2].decode('utf-8-sig')
