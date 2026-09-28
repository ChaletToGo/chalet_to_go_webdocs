from test_i18n import get
import re


def test_preview_and_embedded_view_are_available():
    status, headers, body = get(path='/eco-villa-natal/maquete')
    assert status == 200
    assert headers[b'x-robots-tag'] == b'noindex, nofollow'
    assert 'maquete.js' in body
    assert 'implantacao-basic-seis.svg' in body
    assert body.count('data-unit=') == 6
    assert 'Explorar chalé Basic 06' in body
    assert 'id="loft"' in body
    assert 'body class=""' in body
    status, _, body = get({'embed': '1'}, path='/eco-villa-natal/maquete')
    assert status == 200
    assert 'body class="embedded"' in body


def test_landing_integrates_six_units_and_replaces_old_images():
    status, _, body = get(path='/eco-villa-natal')
    assert status == 200
    assert 'maquete.js' in body
    assert 'villa-scroll.js' in body
    assert 'data-landing="true"' in body
    assert body.count('data-unit=') == 6
    assert 'implantacao-conceitual.jpg' not in body
    assert 'localizacao-referencia.jpg' not in body
    assert 'https://www.google.com/maps/search/?api=1' in body
    assert 'Ver localidade' in body
    assert '≈ 720' in body and '≈ 160' in body
    assert 'pertencem à prancha original de quatro cabanas' in body
    for label in ['QUARTO', 'SALA E COZINHA', 'BANHEIRO', 'VARANDA', 'LAREIRA EXTERNA', 'ESTACIONAMENTO', 'ACESSO']:
        assert label in body
    for material in ['Telha termoacústica', 'Alumínio preto', 'Madeira']:
        assert material in body


def test_landing_orders_banner_model_and_information():
    status, _, body = get(path='/eco-villa-natal')
    assert status == 200
    assert body.index('id="inicio"') < body.index('id="maquete"') < body.index('id="conceito"')
    assert body.count('<h1') == 1


def test_villa_assets_stay_same_origin_behind_http_proxy():
    for path in ['/eco-villa-natal', '/eco-villa-natal/maquete']:
        status, _, body = get(path=path, scheme='http', headers={'host': 'chalettogo.com'})
        assert status == 200
        assert 'http://chalettogo.com' not in body
        assert "import('/static/eco-villa/maquete.js?" in body
        resources = re.findall(r'(?:src|href)="([^\"]+)"', body)
        assert not any(url.startswith('http://') for url in resources)
