from unittest import TestCase
from unittest.mock import patch
from test_i18n import get


class ShowroomTests(TestCase):
    def test_preview_and_proxy_safe_model(self):
        status, headers, body = get(path='/experiencia-3d', scheme='http')
        self.assertEqual(status, 200)
        self.assertEqual(headers[b'x-robots-tag'], b'noindex, nofollow')
        self.assertIn('data-model="/models/', body)
        self.assertNotIn('data-model="http:', body)
        self.assertIn('basico_exterior_modelagem.glb', body)
        self.assertIn('basico_estrutura_modelagem.glb', body)
        self.assertIn('chal%C3%A9_basico/', body)
        self.assertIn('planta_chale_basico.jpg', body)
        self.assertEqual(body.count('<figure>'), 4)

    def test_no_model_still_renders_fallback_page(self):
        with patch('app.showroom.routes.Path.is_file', return_value=False):
            status, _, body = get(path='/experiencia-3d')
        self.assertEqual(status, 200)
        self.assertIn('data-model=""', body)
