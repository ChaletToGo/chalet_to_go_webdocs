import asyncio
import json
import os
import re
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import urlencode

from app.shared.i18n import LOCALES, COUNTRIES, browser_locale
from app.revista.i18n import catalog
from app.main import app


def get(query=None, headers=None, trusted=False, path='/revista'):
    messages = []
    scope = {'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':'GET',
             'scheme':'https','path':path,'raw_path':path.encode(),'root_path':'',
             'query_string':urlencode(query or {}).encode(),
             'headers':[(k.lower().encode(),v.encode()) for k,v in (headers or {}).items()],
             'client':('127.0.0.1',1234),'server':('testserver',443)}
    async def receive():
        return {'type':'http.request','body':b'','more_body':False}
    async def send(message):
        messages.append(message)
    with patch.dict(os.environ, {'TRUST_COUNTRY_HEADER':str(trusted).lower()}):
        asyncio.run(app(scope,receive,send))
    start=next(m for m in messages if m['type']=='http.response.start')
    body=b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body').decode()
    return start['status'],dict(start['headers']),body


class LanguageTests(TestCase):
    def test_country_policy(self):
        for country,locale in {**COUNTRIES,'US':'en'}.items():
            with self.subTest(country=country):
                status,headers,body=get(headers={'CF-IPCountry':country,'Accept-Language':'de'},trusted=True)
                self.assertEqual(status,200)
                self.assertEqual(headers[b'content-language'].decode(),locale)
                self.assertIn(f'<html lang="{locale}">',body)
                self.assertIn('data-locale-source="country"',body)
                self.assertNotIn(b'set-cookie',headers)

    def test_swiss_choices(self):
        for locale in ('rm','de','it','fr','en'):
            _,headers,body=get({'lang':locale},{'CF-IPCountry':'CH'},trusted=True)
            self.assertEqual(headers[b'content-language'].decode(),locale)
            self.assertIn('chalet-language=',headers[b'set-cookie'].decode())
            for code in ('rm','de','it','fr','en'):
                self.assertIn(f'data-language="{code}"',body)

    def test_manual_choice_overrides_saved_and_country(self):
        _,headers,_=get({'lang':'fr'},{'cookie':'chalet-language=it','CF-IPCountry':'BR'},True)
        self.assertEqual(headers[b'content-language'],b'fr')
        _,headers,_=get(headers={'cookie':'chalet-language=it','CF-IPCountry':'CH'},trusted=True)
        self.assertEqual(headers[b'content-language'],b'it')

    def test_automatic_clears_preference(self):
        _,headers,_=get({'lang':'auto'},{'cookie':'chalet-language=it','CF-IPCountry':'CH'},True)
        self.assertEqual(headers[b'content-language'],b'en')
        self.assertIn(b'Max-Age=0',headers[b'set-cookie'])

    def test_untrusted_country_is_ignored(self):
        _,headers,body=get(headers={'CF-IPCountry':'CH','Accept-Language':'pt-BR'})
        self.assertEqual(headers[b'content-language'],b'pt-BR')
        self.assertIn('data-locale-source="browser"',body)

    def test_browser_preferences(self):
        cases={'fr;q=0.3,de;q=0.9':'de','it;q=0,en;q=0.8':'en','pt-PT,pt;q=.8':'pt-PT',
               'de-CH,de;q=.9':'en','rm-CH':'en','pt-BR':'pt-BR','fr-FR':'fr',
               'es,fr;q=.5':'fr','de;q=no, it;q=.5':'it','en;q=0,*;q=0':'en','':'en'}
        for value,expected in cases.items():
            self.assertEqual(browser_locale(value),expected,value)

    def test_invalid_inputs_and_cache(self):
        _,headers,body=get({'lang':'../../secret'},{'cookie':'chalet-language=bad','Accept-Language':'it'})
        self.assertEqual(headers[b'content-language'],b'it')
        self.assertIn(b'no-store',headers[b'cache-control'])
        self.assertNotIn('../../secret',body.split('<title>')[1].split('</title>')[0])

    def test_all_catalogs_have_matching_structure_and_assets(self):
        base=catalog('pt-BR')
        def shape(value):
            if isinstance(value,dict): return {k:shape(v) for k,v in value.items()}
            if isinstance(value,list): return [shape(v) for v in value]
            return type(value).__name__
        for locale in LOCALES:
            with self.subTest(locale=locale):
                data=catalog(locale)
                self.assertEqual(shape(base),shape(data))
                for source,page in zip(base['pages'],data['pages']):
                    for key in ('id','layout','image'):
                        self.assertEqual(source.get(key),page.get(key))
                status,headers,body=get({'lang':locale})
                self.assertEqual(status,200)
                self.assertEqual(body.count('<article '),len(base['pages']))
                self.assertNotRegex(body, r'>\s*undefined\s*<')
                self.assertNotRegex(body, r'(?i)CNS\s+Therapy|Serra do Cip[oó]')
                self.assertIn(data['ui']['language_title'],body)
                self.assertEqual(set(re.findall(r'\{(\w+)\}',data['ui']['announcement'])), {'title','current','total'})

    def test_portuguese_variants(self):
        self.assertIn('equipe',catalog('pt-BR')['pages'][5]['intro'])
        self.assertIn('equipa',catalog('pt-PT')['pages'][5]['intro'])
        self.assertIn('fundo de maneio',catalog('pt-PT')['ui']['investment_body'])
        self.assertNotEqual(catalog('pt-BR')['ui']['fullscreen_enter'],catalog('pt-PT')['ui']['fullscreen_enter'])
