import json
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from test_i18n import get
from app.virtual_cards.routes import load_card


def test_example_and_optional_fields(tmp_path):
    (tmp_path / 'rafael_lima.json').write_text(json.dumps({'nome': 'Rafael Lima', 'cargo': 'Vendas', 'whatsapp': '+553197471887'}), encoding='utf-8')
    with patch('app.virtual_cards.routes.CARD_DIR', tmp_path):
        status, headers, body = get({'lang': 'pt-BR'}, path='/card/rafael_lima')
    assert status == 200
    assert 'Rafael Lima' in body
    assert '/card/rafael_lima/contact.vcf' in body
    assert 'https://wa.me/553197471887' in body
    assert 'Conversar no WhatsApp' in body
    assert 'mailto:' not in body
    assert 'class="profile-photo"' not in body
    assert headers[b'cache-control'] == b'private, no-store'


@pytest.mark.parametrize('photo', ['static/images/ana silva.png', 'images/ana silva.png', '/static/cards/images/ana silva.png', 'app/virtual_cards/static/images/ana silva.png'])
def test_optional_photo(tmp_path, photo):
    images = tmp_path / 'static' / 'images'
    images.mkdir(parents=True)
    (images / 'ana silva.png').write_bytes(b'photo fixture')
    (tmp_path / 'ana.json').write_text(json.dumps({'nome': 'Ana', 'cargo': 'Vendas', 'foto': photo}), encoding='utf-8')
    with patch('app.virtual_cards.routes.CARD_DIR', tmp_path):
        status, _, body = get(path='/card/ana')
    assert status == 200
    assert 'class="profile-photo" src="/static/cards/images/ana%20silva.png"' in body


@pytest.mark.parametrize('photo', ['', 'missing.jpg', '../private.png', 'https://example.com/photo.jpg', 'card.css'])
def test_unavailable_photo_keeps_card_working(tmp_path, photo):
    (tmp_path / 'private.png').write_bytes(b'private')
    (tmp_path / 'ana.json').write_text(json.dumps({'nome': 'Ana', 'cargo': 'Vendas', 'foto': photo}), encoding='utf-8')
    with patch('app.virtual_cards.routes.CARD_DIR', tmp_path):
        status, _, body = get(path='/card/ana')
    assert status == 200
    assert 'class="profile-photo"' not in body


def test_home_without_map():
    status, _, body = get({'lang': 'pt-BR'}, path='/')
    assert status == 200
    assert 'maps.googleapis.com' not in body
    assert 'gmp-map' not in body


def test_maps_and_translated_content(tmp_path):
    from urllib.parse import urlencode
    address = 'Rua São João, 20 & 22, Belo Horizonte - MG'
    data = {'nome': 'Ana Silva', 'cargo': 'Vendas', 'localizacao': address, 'traducoes': {'en': {'cargo': 'Sales', 'sobre': 'Contact our team'}}}
    (tmp_path / 'ana.json').write_text(json.dumps(data), encoding='utf-8')
    with patch('app.virtual_cards.routes.CARD_DIR', tmp_path):
        status, headers, body = get({'lang': 'en'}, path='/card/ana')
        assert status == 200 and headers[b'content-language'] == b'en'
        assert 'Open in maps' in body and '>Sales<' in body and 'Contact our team' in body
        assert urlencode({'api':'1', 'query':address}).replace('&', '&amp;') in body
        assert 'contact.vcf?lang=en' in body
        vcf = get({'lang':'en'}, path='/card/ana/contact.vcf')[2].replace('\r\n ', '')
        assert 'TITLE:Sales' in vcf and 'ADR;TYPE=WORK:;;Rua São João\\, 20 & 22\\, Belo Horizonte - MG;;;;' in vcf
        data['localizacao'] = '  '
        (tmp_path / 'ana.json').write_text(json.dumps(data), encoding='utf-8')
        assert 'google.com/maps' not in get(path='/card/ana')[2]


@pytest.mark.parametrize('country,locale,label', [('BR','pt-BR','Salvar contato'),('PT','pt-PT','Guardar contacto'),('US','en','Save contact'),('DE','de','Kontakt speichern'),('FR','fr','Enregistrer le contact'),('IT','it','Salva contatto'),('CH','en','Save contact')])
def test_country_languages(country, locale, label):
    _, headers, body = get(path='/card/rafael_lima', headers={'CF-IPCountry':country}, trusted=True)
    assert headers[b'content-language'].decode() == locale
    assert label in body and f'<html lang="{locale}">' in body


def test_manual_language_browser_and_cookie():
    _, headers, body = get({'lang':'rm'}, path='/card/rafael_lima', headers={'CF-IPCountry':'BR'}, trusted=True)
    assert 'Memorisar il contact' in body
    assert b'chalet-language=rm' in headers[b'set-cookie']
    assert get(path='/card/rafael_lima', headers={'CF-IPCountry':'BR','Accept-Language':'fr'})[1][b'content-language'] == b'fr'
    assert get(path='/card/rafael_lima', headers={'cookie':'chalet-language=de'})[1][b'content-language'] == b'de'
    assert get({'lang':'auto'}, path='/card/rafael_lima', headers={'cookie':'chalet-language=de','Accept-Language':'it'})[1][b'content-language'] == b'it'


def test_new_json_and_changes_are_available_without_restart():
    with TemporaryDirectory() as directory, patch('app.virtual_cards.routes.CARD_DIR', Path(directory)):
        path = Path(directory) / 'ana_silva.json'
        assert get(path='/card/ana_silva')[0] == 404
        data = {'nome': 'Ana Silva', 'cargo': 'Vendas', 'telefone': '+55 (11) 99999-9999', 'whatsapp': '+5511999999999', 'email': 'ana@example.com'}
        path.write_text(json.dumps(data), encoding='utf-8')
        status, _, body = get(path='/card/ana_silva')
        assert status == 200
        assert 'https://wa.me/5511999999999' in body
        assert 'tel:+5511999999999' in body
        data['nome'] = '<script>alert(1)</script>'
        path.write_text(json.dumps(data), encoding='utf-8')
        body = get(path='/card/ana_silva')[2]
        assert '&lt;script&gt;' in body and '<script>alert' not in body
        path.unlink()
        assert get(path='/card/ana_silva')[0] == 404


@pytest.mark.parametrize('slug', ['../main', '..', 'RAFAEL', 'a/b', 'a\\b', 'a.json'])
def test_invalid_slugs(slug):
    with pytest.raises(HTTPException) as error:
        load_card(slug)
    assert error.value.status_code == 404


@pytest.mark.parametrize('content', ['{', '[]', '{"nome":"Ana"}', '{"nome":"Ana","cargo":"Vendas","site":"javascript:alert(1)"}'])
def test_invalid_file_is_controlled(content):
    with TemporaryDirectory() as directory, patch('app.virtual_cards.routes.CARD_DIR', Path(directory)):
        (Path(directory) / 'invalid.json').write_text(content, encoding='utf-8')
        status, _, body = get(path='/card/invalid')
        assert status == 500
        assert 'temporariamente indisponível' in body
        assert directory not in body


def test_vcard_encoding_escaping_and_line_folding():
    with TemporaryDirectory() as directory, patch('app.virtual_cards.routes.CARD_DIR', Path(directory)):
        (Path(directory) / 'ana.json').write_text(json.dumps({'nome': 'Ana, Silva;', 'cargo': 'Gestão', 'sobre': 'é' * 100, 'email': 'ana@example.com'}), encoding='utf-8')
        status, headers, body = get(path='/card/ana/contact.vcf')
        assert status == 200
        assert b'ana.vcf' in headers[b'content-disposition']
        assert 'FN:Ana\\, Silva\\;' in body
        assert 'EMAIL;TYPE=WORK:ana@example.com\r\n' in body
        assert 'NOTE:' + 'é' * 100 in body.replace('\r\n ', '')
        assert all(len(line.encode('utf-8')) <= 75 for line in body.split('\r\n'))
