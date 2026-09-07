import re
from unittest import TestCase
from test_i18n import get


class ProxyURLTests(TestCase):
    def test_http_upstream_does_not_generate_http_browser_urls(self):
        for path in ('/', '/chales/basic', '/revista'):
            with self.subTest(path=path):
                status, _, body = get({'lang':'pt-BR'}, headers={'host':'chalettogo.com'}, path=path, scheme='http')
                self.assertEqual(status, 200)
                urls = re.findall(r'(?:src|href|srcset|action)="([^"]*)"', body)
                self.assertFalse(any('http://' in value for value in urls))
                self.assertIn('src="/static/', body)
                self.assertIn('href="'+path+'?lang=fr', body)
