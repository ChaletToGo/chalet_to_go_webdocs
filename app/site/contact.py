"""Public consultation requests, stored in the shared TinyDB leads table."""
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.concurrency import run_in_threadpool
from tinydb import Query

from app.shared.database import database
from app.shared.i18n import language_context, apply_language_headers

CONTACT = json.loads(Path(__file__).with_name('contact_content.json').read_text('utf-8'))
router = APIRouter()


class LeadInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=8, max_length=40)
    email: str = Field(default='', max_length=254)
    submission_id: UUID
    website: str = Field(default='', max_length=200)

    @field_validator('name')
    @classmethod
    def valid_name(cls, value):
        if any(ord(c) < 32 for c in value):
            raise ValueError('Invalid name')
        return value

    @field_validator('phone')
    @classmethod
    def valid_phone(cls, value):
        if not re.fullmatch(r'\+?[0-9 ()\-\.]+', value):
            raise ValueError('Invalid phone')
        digits = re.sub(r'\D', '', value)
        if not re.fullmatch(r'[1-9][0-9]{7,14}', digits):
            raise ValueError('Include country code')
        return digits

    @field_validator('email')
    @classmethod
    def valid_email(cls, value):
        if value and not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+", value):
            raise ValueError('Invalid email')
        return value


def save_lead(payload, locale):
    with database('leads') as table:
        # Retrying a submission after a lost response must not create duplicates.
        if not table.contains(Query().submission_id == str(payload.submission_id)):
            table.insert({**payload.model_dump(mode='json', exclude={'website'}),
                          'locale': locale, 'source': '/contato',
                          'created_at': datetime.now(timezone.utc).isoformat()})


@router.post('/api/contact', include_in_schema=False)
async def submit_contact(request: Request):
    context = language_context(request)
    error = CONTACT[context['locale']]['error']
    origin = request.headers.get('origin')
    if origin and (urlsplit(origin).scheme, urlsplit(origin).netloc) != (request.url.scheme, request.url.netloc):
        raise HTTPException(403, error)
    if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
        raise HTTPException(415, error)
    raw = b''
    async for chunk in request.stream():
        raw += chunk
        if len(raw) > 4096:
            raise HTTPException(413, error)
    try:
        payload = LeadInput.model_validate_json(raw)
    except ValueError:
        # Never echo personal details in validation errors.
        raise HTTPException(422, error)
    if not payload.website:
        try:
            await run_in_threadpool(save_lead, payload, context['locale'])
        except Exception:
            logging.getLogger(__name__).error('Contact request could not be stored')
            raise HTTPException(503, error)
    response = JSONResponse({'ok': True}, status_code=201)
    return apply_language_headers(response, request, context)
