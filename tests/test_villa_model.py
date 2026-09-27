from test_i18n import get


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
