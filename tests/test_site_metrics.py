import asyncio
import json
from app.main import app
from app.site.metrics import report

def post(payload, origin='https://www.chalettogo.com'):
    messages=[]
    scope={'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':'POST','scheme':'http',
           'path':'/api/site-metrics','raw_path':b'/api/site-metrics','root_path':'','query_string':b'',
           'headers':[(b'host',b'www.chalettogo.com'),(b'origin',origin.encode()),(b'content-type',b'application/json')],
           'client':('127.0.0.1',1234),'server':('localhost',8000)}
    async def receive():
        return {'type':'http.request','body':json.dumps(payload).encode(),'more_body':False}
    async def send(message):
        messages.append(message)
    asyncio.run(app(scope,receive,send))
    return next(m['status'] for m in messages if m['type']=='http.response.start')

def test_collector_limits_and_opt_out(monkeypatch,tmp_path):
    monkeypatch.setenv('SITE_METRICS_PATH',str(tmp_path/'counts.json'))
    monkeypatch.setenv('SITE_METRICS_ENABLED','true')
    payload={'page':'/','lang':'pt-BR','model':'basic'}
    assert post(payload)==204
    assert report()[0]['whatsapp_clicks']==1
    assert post(payload,origin='https://external.example')==403
    assert post({**payload,'email':'not-accepted'})==422
    assert post({'data':'x'*2000})==413
    monkeypatch.setenv('SITE_METRICS_ENABLED','false')
    assert post(payload)==204
    assert report()[0]['whatsapp_clicks']==1

def test_report_requires_admin_credentials(monkeypatch):
    from test_admin_pages import request
    monkeypatch.setenv('ADMIN_USERNAME','admin')
    monkeypatch.setenv('ADMIN_PASSWORD','test-password')
    assert request('/admin/site-metrics',auth=False)[0]==401
