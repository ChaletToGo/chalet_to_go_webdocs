import asyncio
from io import BytesIO
from unittest import TestCase
from urllib.parse import urlencode
from pypdf import PdfReader
from app.pdf_export import build_pdf
from app.i18n import LOCALES, catalog
from app.main import app


class PdfTests(TestCase):
    def test_all_languages_are_printable_and_exclude_calculator(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                reader=PdfReader(BytesIO(build_pdf(locale)))
                text='\n'.join(page.extract_text() for page in reader.pages)
                data=catalog(locale)
                self.assertEqual(len(reader.pages),14)
                self.assertEqual(reader.trailer['/Root']['/Lang'],locale)
                self.assertIn('Marc Mathys',text)
                self.assertNotIn('CNS Therapy',text)
                self.assertNotIn('Serra do Cipó',text)
                for key in ('input_title','calculate','reset','print_note'):
                    self.assertNotIn(data['finance'][key],text)
                self.assertFalse(reader.get_fields())
                for page in reader.pages:
                    self.assertAlmostEqual(float(page.mediabox.width),595.2756,places=2)
                    self.assertGreater(len(page.extract_text()),100)
                    self.assertNotIn('\ufffd',page.extract_text())

    def test_download_headers_language_and_no_cookie_change(self):
        messages=[]
        scope={'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':'GET','scheme':'https',
               'path':'/revista.pdf','raw_path':b'/revista.pdf','root_path':'','query_string':urlencode({'lang':'fr'}).encode(),
               'headers':[(b'cookie',b'chalet-language=de')],'client':('127.0.0.1',123),'server':('testserver',443)}
        async def receive(): return {'type':'http.request','body':b'','more_body':False}
        async def send(message): messages.append(message)
        asyncio.run(app(scope,receive,send))
        start=next(m for m in messages if m['type']=='http.response.start')
        headers=dict(start['headers'])
        self.assertEqual(start['status'],200)
        self.assertEqual(headers[b'content-type'],b'application/pdf')
        self.assertEqual(headers[b'content-language'],b'fr')
        self.assertIn(b'attachment',headers[b'content-disposition'])
        self.assertIn(b'chalet-to-go-fr.pdf',headers[b'content-disposition'])
        self.assertNotIn(b'set-cookie',headers)
        self.assertTrue(b''.join(m.get('body',b'') for m in messages).startswith(b'%PDF-'))

    def test_unknown_locale_cannot_access_files(self):
        with self.assertRaises(ValueError): build_pdf('../../etc/passwd')
