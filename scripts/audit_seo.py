"""Read-only check of the public site. Usage: python scripts/audit_seo.py https://www.chalettogo.com"""
import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from xml.etree import ElementTree

def audit(origin):
    if urlsplit(origin).scheme not in ('http','https') or urlsplit(origin).path not in ('','/'):
        raise ValueError('Pass an HTTP(S) origin without a path')
    origin=origin.rstrip('/')
    rows=[]
    for path in ('/?lang=pt-BR','/chales/basic?lang=pt-BR','/sobre?lang=pt-BR','/robots.txt','/sitemap.xml','/llms.txt'):
        try:
            with urlopen(Request(origin+path,headers={'User-Agent':'ChaletToGo-SEO-Audit/1.0'}),timeout=25) as response:
                body=response.read().decode('utf-8')
                item={'url':origin+path,'final_url':response.url,'status':response.status,'robots':response.headers.get('X-Robots-Tag','')}
                if path.endswith('sitemap.xml'):
                    item['sitemap_urls']=len(ElementTree.fromstring(body))
                elif '?lang=' in path:
                    item['canonical']=re.findall(r'rel="canonical" href="([^"]+)"',body)
                    item['insecure_assets']=re.findall(r'(?:src|srcset)="http://[^"]+',body)
                    item['h1_count']=len(re.findall(r'<h1(?:\s|>)',body))
                    item['has_schema']='application/ld+json' in body
                rows.append(item)
        except Exception as error:
            rows.append({'url':origin+path,'error':str(error)})
    return rows

if __name__=='__main__':
    print(json.dumps(audit(sys.argv[1]),ensure_ascii=False,indent=2))
