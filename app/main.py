from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .i18n import context_for
from .financials import amount
from .pdf_export import build_pdf
from .i18n import resolve_locale
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Chalet to Go - Revista")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.filters['amount'] = amount


@app.get("/healthz", include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def home(request: Request):
    return RedirectResponse(url=str(request.url_for('revista').replace(query=request.url.query)), status_code=307)


@app.get("/revista", response_class=HTMLResponse)
async def revista(request: Request):
    context = context_for(request)
    response = templates.TemplateResponse(request, "revista.html", context)
    response.headers['Content-Language'] = context['locale']
    response.headers['Cache-Control'] = 'private, no-store'
    response.headers['Vary'] = 'Accept-Language, Cookie, CF-IPCountry'
    if context['locale_source'] == 'explicit':
        response.set_cookie('chalet-language', context['locale'], max_age=31536000,
                            httponly=True, samesite='lax', secure=request.url.scheme == 'https')
    elif request.query_params.get('lang') == 'auto':
        response.delete_cookie('chalet-language', httponly=True, samesite='lax', secure=request.url.scheme == 'https')
    return response


@app.get('/revista.pdf', name='revista_pdf')
def revista_pdf(request: Request):
    locale, _, _ = resolve_locale(request)
    return Response(build_pdf(locale), media_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="chalet-to-go-{locale}.pdf"',
        'Content-Language': locale,
        'Cache-Control': 'private, no-store',
        'Vary': 'Accept-Language, Cookie, CF-IPCountry',
        'X-Content-Type-Options': 'nosniff',
    })
