from unittest import TestCase
from test_i18n import get
from app.site.content import CONTENT
from app.shared.i18n import LOCALES
import json
import re
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urlsplit, parse_qs

class SiteTests(TestCase):
    def test_product_pages_and_sales_links(self):
        for locale in LOCALES:
            for slug,price in [('basic',40000),('standard',65000),('premium',100000)]:
                with self.subTest(locale=locale,slug=slug):
                    status,headers,body=get({'lang':locale},path='/chales/'+slug)
                    self.assertEqual(status,200)
                    self.assertNotIn('/revista',body)
                    self.assertIn(f'https://www.chalettogo.com/chales/{slug}?lang={locale}',body)
                    schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',body).group(1))
                    product=next(item for item in schema['@graph'] if item['@type']=='Product')
                    self.assertEqual(product['offers']['price'],price)
                    self.assertEqual(product['offers']['priceCurrency'],'CHF')
                    links=re.findall(r'class="[^"]*sales-action[^"]*" href="([^"]+)"',body)
                    self.assertGreaterEqual(len(links),3)
                    for link in links:
                        parsed=urlsplit(unescape(link))
                        self.assertEqual(parsed.netloc,'wa.me')
                        self.assertEqual(parsed.path,'/5538998840910')
                        self.assertIn(slug.lower(),parse_qs(parsed.query)['text'][0].lower())
        self.assertEqual(get(path='/chales/unknown')[0],404)

    def test_search_discovery_and_local_noindex(self):
        status,headers,body=get(path='/sitemap.xml')
        self.assertEqual(status,200)
        root=ET.fromstring(body)
        self.assertEqual(len(root),49)
        for entry in root:
            self.assertTrue(entry[0].text.startswith('https://www.chalettogo.com/'))
            self.assertEqual(len(entry.findall('{http://www.w3.org/1999/xhtml}link')),8)
        self.assertIn('Disallow: /',get(path='/robots.txt')[2])
        self.assertIn('noindex',get(path='/')[1][b'x-robots-tag'].decode())
        self.assertIn('Sitemap: https://www.chalettogo.com/sitemap.xml',get(headers={'host':'www.chalettogo.com'},path='/robots.txt')[2])
        self.assertIn('index, follow',get(headers={'host':'www.chalettogo.com'},path='/')[1][b'x-robots-tag'].decode())

    def test_site_has_independent_translated_pages(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                status,headers,body=get({'lang':locale},path='/')
                self.assertEqual(status,200)
                self.assertEqual(headers[b'content-language'].decode(),locale)
                self.assertIn(CONTENT[locale]['hero'],body)
                self.assertIn('/static/site/css/site.css',body)
                self.assertIn('/static/brand/brand.css',body)
                self.assertIn('/static/images/Logomarca.svg',body)
                self.assertNotIn('/revista',body)
                self.assertIn('https://wa.me/5538998840910?',body)
                self.assertEqual(body.count('alt="Suisse Garantie"'),4)
                self.assertLess(body.index('id="produto"'),body.index('id="chales"'))
                self.assertLess(body.index('id="madeira"'),body.index('id="chales"'))
                self.assertEqual(body.count('class="gallery-card"'),6)
                self.assertNotIn('reader.js',body)
                self.assertNotIn('finance-form',body)

    def test_asset_routes_and_legacy_urls(self):
        for path in ['/static/site/css/site.css','/static/brand/brand.css',
                     '/static/revista/css/main.css','/static/revista/js/reader.js',
                     '/static/css/main.css','/static/js/reader.js']:
            with self.subTest(path=path):
                self.assertEqual(get(path=path)[0],200)

    def test_same_country_policy_for_site(self):
        status,headers,body=get(headers={'CF-IPCountry':'CH','Accept-Language':'fr'},trusted=True,path='/')
        self.assertEqual(headers[b'content-language'],b'en')
        self.assertIn(CONTENT['en']['hero'],body)
