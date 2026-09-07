"""Public URLs and search metadata, independent of request Host headers."""
import os
from urllib.parse import urlsplit, urlencode
from ..shared.i18n import LOCALES

def origin():
    value=os.getenv('SITE_URL','https://www.chalettogo.com').rstrip('/')
    parsed=urlsplit(value)
    if parsed.scheme!='https' or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username:
        raise ValueError('SITE_URL must be a public HTTPS origin without path or credentials')
    return value

def public_url(path='/', locale=None):
    return origin()+path+('?' + urlencode({'lang':locale}) if locale else '')

def indexable(request):
    return os.getenv('SITE_INDEXABLE','true').lower()=='true' and request.url.hostname==urlsplit(origin()).hostname

def metadata(request,text,locale,product=None):
    path=f"/chales/{product['slug']}" if product else '/'
    canonical=public_url(path,locale)
    organization={'@type':'Organization','@id':origin()+'/#organization','name':'Chalet to Go',
                  'url':origin()+'/', 'logo':public_url('/static/images/Logomarca.png')}
    page={'@type':'WebPage','@id':canonical+'#page','url':canonical,'inLanguage':locale,
          'name':text['seo_title'] if not product else text['product_title'].format(model=product['name']),
          'isPartOf':{'@id':origin()+'/#website'}}
    website={'@type':'WebSite','@id':origin()+'/#website','name':'Chalet to Go','url':origin()+'/',
             'publisher':{'@id':organization['@id']}}
    graph=[organization,website,page]
    image_slug=product['slug'] if product else 'premium'
    if product:
        graph.append({'@type':'Product','@id':canonical+'#product','name':'Chalet to Go '+product['name'],
          'description':product['description'],'image':public_url(f"/static/site/images/{product['slug']}-1440.webp"),
          'brand':{'@type':'Brand','name':'Chalet to Go'},'url':canonical,
          'offers':{'@type':'Offer','url':canonical,'priceCurrency':'CHF','price':product['price'],
                    'seller':{'@id':organization['@id']}}})
        page['mainEntity']={'@id':canonical+'#product'}
    return {'canonical':canonical,'alternates':[(code,public_url(path,code)) for code in LOCALES],
            'default_url':public_url(path,'en'),'title':page['name'],
            'description':product['description'] if product else text['seo_description'],
            'image':public_url(f'/static/site/images/{image_slug}-1440.webp'),
            'robots':'index, follow, max-image-preview:large' if indexable(request) else 'noindex, nofollow',
            'schema':{'@context':'https://schema.org','@graph':graph}}
