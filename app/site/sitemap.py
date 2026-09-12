"""Canonical public pages and images actually displayed on those pages."""
from xml.etree.ElementTree import Element, SubElement, tostring, register_namespace

from ..shared.i18n import LOCALES
from .content import PRODUCTS
from .discovery import PAGES
from .seo import public_url

GALLERY = [('interior-3', 'inside', 1122, 1402), ('exterior', 'outside', 900, 673),
           ('interior-2', 'inside', 1464, 1075), ('living', 'inside', 1151, 1139),
           ('interior-1', 'inside', 1033, 1522), ('premium', 'plan', 1536, 1024)]
SM = 'http://www.sitemaps.org/schemas/sitemap/0.9'
XHTML = 'http://www.w3.org/1999/xhtml'
IMAGE = 'http://www.google.com/schemas/sitemap-image/1.1'
register_namespace('', SM)
register_namespace('xhtml', XHTML)
register_namespace('image', IMAGE)


def build_sitemap():
    root = Element(f'{{{SM}}}urlset')
    pages = {'/': list(dict.fromkeys([p['slug'] for p in PRODUCTS] + [p[0] for p in GALLERY]))}
    pages.update({f"/chales/{p['slug']}": [p['slug']] for p in PRODUCTS})
    pages.update({'/' + slug: [] for slug in PAGES})
    for path, images in pages.items():
        for locale in LOCALES:
            entry = SubElement(root, f'{{{SM}}}url')
            SubElement(entry, f'{{{SM}}}loc').text = public_url(path, locale)
            for language in [*LOCALES, 'x-default']:
                SubElement(entry, f'{{{XHTML}}}link', rel='alternate', hreflang=language,
                           href=public_url(path, 'en' if language == 'x-default' else language))
            for slug in images:
                image = SubElement(entry, f'{{{IMAGE}}}image')
                SubElement(image, f'{{{IMAGE}}}loc').text = public_url(f'/static/site/images/{slug}-1440.webp')
    # Omit lastmod until editorial modification dates are maintained reliably.
    return tostring(root, encoding='utf-8', xml_declaration=True)
