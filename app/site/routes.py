import os
import re
from pathlib import Path
from urllib.parse import urlencode
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from fastapi.templating import Jinja2Templates
from ..shared.i18n import language_context, apply_language_headers, LOCALES
from .content import CONTENT, PRODUCTS
from .seo import metadata, public_url, indexable, canonical_redirect
from .discovery import PAGES, page_content, resources
from . import metrics
from .company import company_context
from .maps import map_context
from .sitemap import build_sitemap, GALLERY
from urllib.parse import urlsplit
import logging
from starlette.concurrency import run_in_threadpool
from ..shared.urls import local_url

router=APIRouter()
templates=Jinja2Templates(directory=Path(__file__).parent/'templates')
templates.env.filters['local_url'] = local_url

def amount(value,locale):
    separator=',' if locale=='en' else '’' if locale=='rm' else '\u202f' if locale in ('fr','pt-PT') else '.'
    return f'{value:,.0f}'.replace(',',separator)
templates.env.filters['amount']=amount

def whatsapp(message):
    number=os.getenv('WHATSAPP_NUMBER','5538998840910').strip().lstrip('+')
    if not re.fullmatch(r'[1-9][0-9]{7,14}',number):
        raise ValueError('WHATSAPP_NUMBER must contain country code and digits only')
    return 'https://wa.me/'+number+'?'+urlencode({'text':message})

def render(request,slug=None,article_slug=None):
    redirect=canonical_redirect(request)
    if redirect:
        return redirect
    context=language_context(request)
    context['location_map'] = map_context(context['locale']) if not slug and not article_slug else None
    locale=context['locale']
    context['company'] = company_context(locale)
    text=CONTENT[locale]
    products=[{**p,'description':text['models'][i],'benefit':text['benefits'][i],
               'whatsapp':whatsapp(text['plan_message'].format(model=p['name']))} for i,p in enumerate(PRODUCTS)]
    selected=next((p for p in products if p['slug']==slug),None)
    if slug and not selected:
        raise HTTPException(status_code=404)
    article=page_content(article_slug,locale) if article_slug else None
    context.update(text=text,products=products,product=selected,article=article,gallery=GALLERY,resources=resources(locale),metrics_enabled=metrics.enabled(),whatsapp=whatsapp(text['message']),
                   seo=metadata(request,text,locale,selected,article))
    response=templates.TemplateResponse(request,'discovery.html' if article else 'product.html' if selected else 'index.html',context)
    response.headers['X-Robots-Tag']=context['seo']['robots']
    return apply_language_headers(response,request,context)

@router.get('/',response_class=HTMLResponse,name='site_home')
async def home(request: Request):
    return render(request)

@router.get('/chales/{slug}',response_class=HTMLResponse,name='site_product')
async def product_page(request: Request,slug:str):
    return render(request,slug)

@router.get('/robots.txt',response_class=PlainTextResponse,include_in_schema=False)
def robots(request: Request):
    redirect=canonical_redirect(request)
    if redirect:
        return redirect
    if not indexable(request):
        return 'User-agent: *\nDisallow: /\n'
    # Search crawlers, including AI search, inherit the public Allow rule.
    return ('User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\n'
            'Disallow: /docs\nDisallow: /redoc\nDisallow: /openapi.json\n'
            'Sitemap: '+public_url('/sitemap.xml')+'\n')

@router.get('/sitemap.xml',include_in_schema=False)
def sitemap(request: Request):
    redirect=canonical_redirect(request)
    if redirect:
        return redirect
    return Response(build_sitemap(), media_type='application/xml')

@router.get('/sobre',response_class=HTMLResponse)
async def about(request: Request):
    return render(request,article_slug='sobre')

@router.get('/perguntas-frequentes',response_class=HTMLResponse)
async def faq(request: Request):
    return render(request,article_slug='perguntas-frequentes')

@router.get('/chales-para-hospedagem',response_class=HTMLResponse)
async def hospitality(request: Request):
    return render(request,article_slug='chales-para-hospedagem')

@router.get('/llms.txt',response_class=PlainTextResponse,include_in_schema=False)
def llms(request: Request):
    redirect=canonical_redirect(request)
    if redirect:
        return redirect
    lines=['# Chalet To GO','', '> Timber chalets and tiny houses. Official product and company information.',
           '', '## Products']
    for item in PRODUCTS:
        lines.append(f"- [{item['name']}]({public_url('/chales/'+item['slug'],'en')}): CHF {item['price']:,}; scope and terms in the proposal.")
    lines += ['', '## Company and buying information']
    lines += [f"- [{item['title']}]({public_url('/'+item['slug'],'en')})" for item in resources('en')]
    lines += ['', '## Company facts',
              'Name: Chalet To GO.',
              'Company address: Rte de Porrentruy 8, 2800 Delémont, Switzerland.',
              'Brazil: initial production setup in Minas Caixa, Belo Horizonte; team prepared for the first unit.',
              'Timber: kiln-dried, treated pine. Optional Generali coverage for Swiss timber chalets is available at extra cost, up to 20 years subject to contract. Brazilian timber warranty: 6 months, subject to proposal terms.',
              '', '## Languages', ', '.join(LOCALES), '', 'Specifications and warranty availability must be confirmed in the quotation.']
    return '\n'.join(lines)+'\n'

@router.post('/api/site-metrics',include_in_schema=False)
async def capture_click(request: Request):
    if not metrics.enabled():
        return Response(status_code=204)
    origin=request.headers.get('origin','')
    if not origin or urlsplit(origin).netloc!=request.url.netloc:
        raise HTTPException(403,'Invalid origin')
    raw=b''
    async for chunk in request.stream():
        raw+=chunk
        if len(raw)>1024:
            raise HTTPException(413,'Payload too large')
    try:
        click=metrics.Click.model_validate_json(raw)
    except ValueError:
        raise HTTPException(422,'Invalid event')
    try:
        await run_in_threadpool(metrics.record,click)
    except Exception:
        logging.getLogger(__name__).warning('Site click count could not be stored')
        return Response(status_code=503)
    return Response(status_code=204,headers={'Cache-Control':'no-store'})
