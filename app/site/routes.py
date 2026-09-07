import os
import re
from pathlib import Path
from urllib.parse import urlencode
from xml.sax.saxutils import escape
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from fastapi.templating import Jinja2Templates
from ..shared.i18n import language_context, apply_language_headers, LOCALES
from .content import CONTENT, PRODUCTS
from .seo import metadata, public_url, indexable

router=APIRouter()
templates=Jinja2Templates(directory=Path(__file__).parent/'templates')

def amount(value,locale):
    separator=',' if locale=='en' else '’' if locale=='rm' else '\u202f' if locale in ('fr','pt-PT') else '.'
    return f'{value:,.0f}'.replace(',',separator)
templates.env.filters['amount']=amount

def whatsapp(message):
    number=os.getenv('WHATSAPP_NUMBER','5538998840910').strip().lstrip('+')
    if not re.fullmatch(r'[1-9][0-9]{7,14}',number):
        raise ValueError('WHATSAPP_NUMBER must contain country code and digits only')
    return 'https://wa.me/'+number+'?'+urlencode({'text':message})

def render(request,slug=None):
    context=language_context(request)
    locale=context['locale']
    text=CONTENT[locale]
    products=[{**p,'description':text['models'][i],'benefit':text['benefits'][i],
               'whatsapp':whatsapp(text['plan_message'].format(model=p['name']))} for i,p in enumerate(PRODUCTS)]
    selected=next((p for p in products if p['slug']==slug),None)
    if slug and not selected:
        raise HTTPException(status_code=404)
    context.update(text=text,products=products,product=selected,whatsapp=whatsapp(text['message']),
                   seo=metadata(request,text,locale,selected))
    response=templates.TemplateResponse(request,'product.html' if selected else 'index.html',context)
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
    if not indexable(request):
        return 'User-agent: *\nDisallow: /\n'
    return 'User-agent: *\nAllow: /\nSitemap: '+public_url('/sitemap.xml')+'\n'

@router.get('/sitemap.xml',include_in_schema=False)
def sitemap():
    entries=[]
    for path in ['/']+[f"/chales/{p['slug']}" for p in PRODUCTS]:
        alternate=''.join(f'<xhtml:link rel="alternate" hreflang="{lang}" href="{escape(public_url(path,lang))}"/>' for lang in LOCALES)
        alternate+=f'<xhtml:link rel="alternate" hreflang="x-default" href="{escape(public_url(path,"en"))}"/>'
        for lang in LOCALES:
            entries.append('<url><loc>'+escape(public_url(path,lang))+'</loc>'+alternate+'</url>')
    return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+''.join(entries)+'</urlset>',media_type='application/xml')
