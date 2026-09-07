from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from .i18n import context_for
from .pdf_export import build_pdf
from ..shared.i18n import resolve_locale, apply_language_headers
from .financials import amount
from ..shared.urls import local_url

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')
templates.env.filters['amount'] = amount
templates.env.filters['local_url'] = local_url

@router.get('/revista', response_class=HTMLResponse, name='revista')
async def revista(request: Request):
    context = context_for(request)
    return apply_language_headers(templates.TemplateResponse(request,'revista.html',context),request,context)

@router.get('/revista.pdf', name='revista_pdf')
def revista_pdf(request: Request):
    locale, _, _ = resolve_locale(request)
    return Response(build_pdf(locale), media_type='application/pdf', headers={
        'Content-Disposition':f'attachment; filename="chalet-to-go-{locale}.pdf"',
        'Content-Language':locale, 'Cache-Control':'private, no-store',
        'Vary':'Accept-Language, Cookie, CF-IPCountry','X-Content-Type-Options':'nosniff'})
