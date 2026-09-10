"""Public URLs and search metadata, independent of request Host headers."""
import os
from .company import NAME, ADDRESS, profiles
from urllib.parse import urlsplit, urlencode
from ..shared.i18n import LOCALES
from fastapi.responses import RedirectResponse

def canonical_redirect(request):
    """Only redirect the alternate public hostname; never localhost or arbitrary Hosts."""
    host = urlsplit(origin()).hostname
    alternate = host[4:] if host.startswith('www.') else 'www.' + host
    if request.url.hostname == alternate:
        target = origin() + request.url.path
        if request.url.query:
            target += '?' + request.url.query
        return RedirectResponse(target, status_code=308)
    return None

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

def metadata(request,text,locale,product=None,article=None):
    path=f"/{article['slug']}" if article else f"/chales/{product['slug']}" if product else '/'
    canonical=public_url(path,locale)
    organization={'@type':'Organization','@id':origin()+'/#organization','name':'Chalet To GO','alternateName':'Chalettogo',
                  'url':origin()+'/', 'logo':public_url('/static/images/Logomarca.png')}
    organization['contactPoint']={'@type':'ContactPoint','contactType':'sales',
        'telephone':'+'+os.getenv('WHATSAPP_NUMBER','5538998840910').lstrip('+')}
    organization['address'] = ADDRESS.copy()
    official_profiles = profiles()
    if official_profiles:
        organization['sameAs'] = [item['url'] for item in official_profiles]
    page={'@type':'WebPage','@id':canonical+'#page','url':canonical,'inLanguage':locale,
          'name':article['title']+' | Chalet To GO' if article else text['seo_title'] if not product else text['product_title'].format(model=product['name']),
          'isPartOf':{'@id':origin()+'/#website'}}
    website={'@type':'WebSite','@id':origin()+'/#website','name':NAME,'alternateName':'Chalettogo','url':origin()+'/',
             'publisher':{'@id':organization['@id']}}
    graph=[organization,website,page]
    if path != '/':
        graph.append({'@type':'BreadcrumbList','itemListElement':[
            {'@type':'ListItem','position':1,'name':text['home'],'item':public_url('/',locale)},
            {'@type':'ListItem','position':2,'name':product['name'] if product else article['title'],'item':canonical}]})
    if article and article['slug']=='sobre':
        page['@type']='AboutPage'
        page['about']={'@id':organization['@id']}
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
            'description':article['intro'] if article else product['description'] if product else text['seo_description'],
            'image':public_url(f'/static/site/images/{image_slug}-1440.webp'),
            'robots':'index, follow, max-image-preview:large' if indexable(request) else 'noindex, nofollow',
            'schema':{'@context':'https://schema.org','@graph':graph},
            'google_verification':os.getenv('GOOGLE_SITE_VERIFICATION',''),
            'bing_verification':os.getenv('BING_SITE_VERIFICATION','')}
