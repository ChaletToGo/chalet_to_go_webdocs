import re
from unittest import TestCase
from test_i18n import get
from app.shared.urls import local_url
from hashlib import sha256
from pathlib import Path


class ProxyURLTests(TestCase):
    def test_asset_version_matches_shipped_file(self):
        for asset in ('css/site.css', 'js/header.js'):
            digest = sha256((Path('app/site/static')/asset).read_bytes()).hexdigest()[:12]
            self.assertEqual(local_url('http://chalettogo.com/static/site/'+asset), '/static/site/'+asset+'?v='+digest)
        self.assertEqual(local_url('http://chalettogo.com/?lang=fr'), '/?lang=fr')

    def test_http_upstream_does_not_generate_http_browser_urls(self):
        for path in ('/', '/chales/basic', '/revista'):
            with self.subTest(path=path):
                status, _, body = get({'lang':'pt-BR'}, headers={'host':'chalettogo.com'}, path=path, scheme='http')
                self.assertEqual(status, 200)
                urls = re.findall(r'(?:src|href|srcset|action)="([^"]*)"', body)
                self.assertFalse(any('http://' in value for value in urls))
                self.assertIn('src="/static/', body)
                self.assertIn('href="'+path+'?lang=fr', body)
