from app.site.company import profiles, company_context
from app.site.seo import metadata
from app.site.content import CONTENT
from starlette.requests import Request

def test_profiles_reject_unsafe_links(monkeypatch):
    monkeypatch.setenv('SITE_OFFICIAL_PROFILES', 'javascript:alert(1),https://example.com/profile,https://example.com/profile,https://user:password@example.com')
    assert profiles() == [{'url': 'https://example.com/profile', 'label': 'example.com'}]

def test_identity_matches_visible_address(monkeypatch):
    monkeypatch.delenv('SITE_OFFICIAL_PROFILES', raising=False)
    request = Request({'type':'http', 'method':'GET', 'path':'/', 'headers':[(b'host',b'www.chalettogo.com')], 'scheme':'https', 'query_string':b''})
    graph = metadata(request, CONTENT['en'], 'en')['schema']['@graph']
    assert graph[0]['address']['addressLocality'] == 'Delémont'
    assert 'sameAs' not in graph[0]
    assert graph[1]['name'] == company_context('en')['name']
    assert 'Rte de Porrentruy 8' in company_context('pt-BR')['address']
