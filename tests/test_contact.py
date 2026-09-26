import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest

from test_admin_pages import request, settings
from test_i18n import get
from app.shared.database import database
from app.shared.i18n import LOCALES
from app.site.contact import CONTACT, LeadInput, save_lead


def payload(**changes):
    return {'name': 'Contato Teste', 'phone': '+55 (38) 99884-0910',
            'submission_id': str(uuid4()), **changes}


def test_contact_languages_and_navigation():
    for locale in LOCALES:
        status, headers, body = get({'lang': locale}, path='/contato')
        assert status == 200
        assert headers[b'content-language'].decode() == locale
        assert CONTACT[locale]['title'] in body
        assert f'/contato?lang={locale}' in body
        assert f'/api/contact?lang={locale}' in body
        assert f'/contato?lang={locale}' in get({'lang': locale}, path='/')[2]
    assert get(headers={'CF-IPCountry': 'BR'}, trusted=True, path='/contato')[1][b'content-language'] == b'pt-BR'
    assert get(headers={'cookie': 'chalet-language=fr'}, path='/contato')[1][b'content-language'] == b'fr'


def test_submission_storage_retry_and_private_admin():
    data = payload()
    for _ in range(2):
        status, headers, body = request('/api/contact?lang=pt-BR', 'POST', data, auth=False)
        assert status == 201 and json.loads(body) == {'ok': True}
        assert b'no-store' in headers[b'cache-control']
    with database('leads') as table:
        assert len(table) == 1
        row = table.all()[0]
        assert row['phone'] == '5538998840910'
        assert row['email'] == '' and row['locale'] == 'pt-BR'
    for path in ['/admin', '/admin/leads', '/admin/metrics', '/admin/qrcodes']:
        assert request(path, auth=False)[0] == 401
        status, headers, _ = request(path)
        assert status == 200 and headers[b'cache-control'] == b'no-store'
    assert b'Contato Teste' in request('/admin/leads')[2]
    assert b'Contato Teste' not in request('/admin/leads?search=missing')[2]


@pytest.mark.parametrize('changes', [{'name': ' '}, {'phone': '123'}, {'phone': 'abcdefghij'},
                                    {'email': 'bad@'}, {'name': 'A'*121}])
def test_invalid_leads_not_saved(changes):
    assert request('/api/contact', 'POST', payload(**changes), auth=False)[0] == 422
    with database('leads') as table:
        assert len(table) == 0


def test_bot_trap_and_size_limit():
    assert request('/api/contact', 'POST', payload(website='spam'), auth=False)[0] == 201
    assert request('/api/contact', 'POST', payload(name='A'*5000), auth=False)[0] == 413
    with database('leads') as table:
        assert len(table) == 0


def test_parallel_leads_keep_qrcodes_and_escape_html():
    with database() as table:
        table.insert({'code': 'existing'})
    data = LeadInput(**payload(name='<script>alert(1)</script>', email='test@example.com'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: save_lead(data, 'en'), range(12)))
    with database('leads') as table:
        assert len(table) == 1
    with database() as table:
        assert table.all()[0]['code'] == 'existing'
    html = request('/admin/leads')[2].decode()
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html


@pytest.mark.parametrize('host', ['www.chalettogo.com', 'chalet-web:8000'])
def test_https_contact_behind_http_proxy(monkeypatch, host):
    monkeypatch.setenv('SITE_URL', 'https://www.chalettogo.com')
    status, _, _ = request('/api/contact?lang=pt-BR', 'POST', payload(), auth=False,
        scheme='http', extra_headers={'host': host, 'origin': 'https://www.chalettogo.com'})
    assert status == 201
    with database('leads') as table:
        assert len(table) == 1


@pytest.mark.parametrize('origin', ['https://evil.example', 'null',
    'https://www.chalettogo.com.evil.example', 'https://www.chalettogo.com:444'])
def test_contact_rejects_foreign_origins(monkeypatch, origin):
    monkeypatch.setenv('SITE_URL', 'https://www.chalettogo.com')
    status, _, _ = request('/api/contact', 'POST', payload(), auth=False,
        scheme='http', extra_headers={'host': 'chalet-web:8000', 'origin': origin,
                                     'x-forwarded-host': 'evil.example', 'x-forwarded-proto': 'https'})
    assert status == 403
    with database('leads') as table:
        assert len(table) == 0


def test_contact_local_same_origin():
    assert request('/api/contact', 'POST', payload(), auth=False, scheme='http',
        extra_headers={'host': 'localhost:8000', 'origin': 'http://localhost:8000'})[0] == 201


def test_home_waitlist_uses_shared_form_and_records_source():
    for locale in LOCALES:
        _, _, html = get({'lang': locale}, path='/')
        assert html.count('id="contact-form"') == 1
        assert CONTACT[locale]['title'] in html
        assert 'name="source" value="/"' in html
        assert html.index('id="fila-de-espera"') < html.index('<footer>')
    status, _, _ = request('/api/contact?lang=pt-BR', 'POST', payload(source='/'), auth=False)
    assert status == 201
    with database('leads') as table:
        assert table.all()[0]['source'] == '/'
