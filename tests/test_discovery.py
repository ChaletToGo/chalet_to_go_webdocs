import json
import re
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from test_i18n import get
from app.site.discovery import PAGES
from app.site.metrics import Click, record, report
from app.shared.i18n import LOCALES

class DiscoveryTests(TestCase):
    def test_alternate_host_redirect_preserves_language(self):
        for path in ['/', '/chales/basic', '/sobre', '/robots.txt', '/sitemap.xml', '/llms.txt']:
            status,headers,_=get({'lang':'fr'},headers={'host':'chalettogo.com'},path=path)
            self.assertEqual(status,308)
            self.assertEqual(headers[b'location'].decode(),'https://www.chalettogo.com'+path+'?lang=fr')
        with patch.dict('os.environ', {'SITE_URL':'https://chalettogo.com'}):
            self.assertEqual(get(headers={'host':'www.chalettogo.com'},path='/')[0],308)
            self.assertEqual(get(headers={'host':'chalettogo.com'},path='/')[0],200)

    def test_guides_have_language_and_matching_metadata(self):
        for slug in PAGES:
            for lang in LOCALES:
                status,headers,body=get({'lang':lang},path='/'+slug)
                self.assertEqual(status,200)
                self.assertEqual(headers[b'content-language'].decode(),lang)
                self.assertEqual(body.count('<h1'),1)
                self.assertIn(f'https://www.chalettogo.com/{slug}?lang={lang}',body)
                graph=json.loads(re.search(r'application/ld\+json">(.*?)</script>',body).group(1))['@graph']
                self.assertTrue(any(item['@type']=='BreadcrumbList' for item in graph))
                self.assertNotIn('/revista',body)

    def test_verification_is_opt_in_and_escaped(self):
        with patch.dict('os.environ',{'GOOGLE_SITE_VERIFICATION':'abc"<test>','BING_SITE_VERIFICATION':'bing-token'}):
            body=get(path='/')[2]
            self.assertIn('google-site-verification',body)
            self.assertNotIn('content="abc"<test>',body)
            self.assertIn('bing-token',body)

    def test_public_discovery_rules(self):
        rules=get(headers={'host':'www.chalettogo.com'},path='/robots.txt')[2]
        self.assertIn('Allow: /',rules)
        self.assertIn('Disallow: /admin',rules)
        text=get(path='/llms.txt')[2]
        self.assertIn('40,000',text)
        self.assertNotIn('15,000',text)

    def test_aggregate_counts_do_not_store_personal_fields(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ',{'SITE_METRICS_PATH':str(Path(directory)/'metrics.json')}):
            click=Click(page='/chales/basic',lang='pt-BR',model='basic')
            record(click); record(click)
            rows=report()
            self.assertEqual(rows[0]['whatsapp_clicks'],2)
            self.assertEqual(set(rows[0]),{'date','page','lang','model','whatsapp_clicks'})
            with self.assertRaises(ValueError):
                Click(page='/admin',lang='pt-BR')
