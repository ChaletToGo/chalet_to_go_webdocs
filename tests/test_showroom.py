import asyncio
import gzip
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from app.showroom.cache import ModelFiles, file_version
from test_i18n import get

class ShowroomTests(TestCase):
    def test_draft_redirects_to_product(self):
        status, headers, _ = get({'lang': 'pt-BR'}, path='/experiencia-3d')
        self.assertEqual(status, 301)
        self.assertEqual(headers[b'location'], b'/chales/basic?lang=pt-BR')

    def test_product_and_proxy_safe_model(self):
        status, headers, body = get(path='/chales/basic', scheme='http')
        self.assertEqual(status, 200)
        self.assertEqual(headers[b'x-robots-tag'], b'noindex, nofollow')
        self.assertIn('data-model="/models/', body)
        self.assertIn('?v=', body)
        self.assertIn('basico_estrutura_modelagem.glb', body)
        self.assertIn('chal%C3%A9_basico/', body)
        self.assertIn('planta_chale_basico.jpg', body)
        self.assertEqual(body.count('<figure>'), 4)
        self.assertEqual(body.count('role="tab"'), 4)
        self.assertIn('data-panel="overview"', body)
        self.assertNotIn('EXPERIMENTO', body)
        status, headers, body = get(path='/chales/basic', headers={'host':'www.chalettogo.com'})
        self.assertIn(b'index, follow', headers[b'x-robots-tag'])
        self.assertIn('rel="canonical" href="https://www.chalettogo.com/chales/basic?lang=en"',body)

    def test_missing_assets_keep_product_available(self):
        with TemporaryDirectory() as directory, patch('app.showroom.routes.ASSETS', Path(directory)):
            status, _, body = get(path='/chales/basic')
        self.assertEqual(status, 200)
        self.assertIn('data-model=""', body)

class ModelCacheTests(TestCase):
    def test_compression_conditional_range_and_invalidation(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'test.glb'
            payload = b'glTF' + b'0123456789' * 1000
            path.write_bytes(payload)
            app = ModelFiles(directory=directory)
            def request(headers=None, version=None, method='GET'):
                messages=[]
                scope={'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':method,'scheme':'http','path':'/test.glb','root_path':'','query_string':('v='+version).encode() if version else b'','headers':[(k.lower().encode(),v.encode()) for k,v in (headers or {}).items()]}
                async def receive(): return {'type':'http.request','body':b''}
                async def send(message): messages.append(message)
                asyncio.run(app(scope,receive,send))
                start=messages[0]
                return start['status'],dict(start['headers']),b''.join(m.get('body',b'') for m in messages)
            version=file_version(path.stat())
            status,headers,body=request({'Accept-Encoding':'gzip'},version)
            self.assertEqual(gzip.decompress(body),payload)
            self.assertIn(b'immutable',headers[b'cache-control'])
            self.assertEqual(len(app._cache),1)
            cached=next(iter(app._cache.values()))
            self.assertEqual(request({'Accept-Encoding':'gzip'},version)[2],cached)
            self.assertEqual(request({'If-None-Match':headers[b'etag'].decode()},version)[0],304)
            status,headers,body=request({'Range':'bytes=0-3','Accept-Encoding':'gzip'},version)
            self.assertEqual((status,body),(206,b'glTF'))
            self.assertEqual(request({'Accept-Encoding':'gzip;q=0'},version)[2],payload)
            self.assertEqual(request({'Accept-Encoding':'gzip'},version,method='HEAD')[2],b'')
            path.write_bytes(payload+b'new')
            status,headers,body=request({'Accept-Encoding':'gzip'},version)
            self.assertNotIn(b'immutable',headers[b'cache-control'])
            self.assertEqual(gzip.decompress(body),payload+b'new')
            self.assertLessEqual(app._bytes,app.budget)
