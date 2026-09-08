import json
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from test_i18n import get
from app.virtual_cards.routes import load_card


def test_example_and_optional_fields():
    status, headers, body = get(path='/card/rafael_lima')
    assert status == 200
    assert 'Rafael Lima' in body
    assert '/card/rafael_lima/contact.vcf' in body
    assert 'https://wa.me/553197471887' in body
    assert 'Conversar no WhatsApp' in body
    assert 'mailto:' not in body
    assert headers[b'cache-control'] == b'no-store'


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
