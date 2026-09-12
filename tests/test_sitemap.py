from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from xml.etree.ElementTree import fromstring

from test_i18n import get
from app.site.sitemap import SM, XHTML, IMAGE


def test_sitemap_canonical_pages_alternates_and_images():
    status, _, xml = get(path='/sitemap.xml')
    assert status == 200
    entries = fromstring(xml).findall(f'{{{SM}}}url')
    locations = [entry.findtext(f'{{{SM}}}loc') for entry in entries]
    assert len(locations) == len(set(locations)) == 49
    for entry, location in zip(entries, locations):
        url = urlsplit(location)
        status, _, html = get({k: v[0] for k, v in parse_qs(url.query).items()}, path=url.path,
                              headers={'host': url.netloc})
        assert status == 200
        assert f'rel="canonical" href="{location}"' in html
        assert 'noindex' not in html
        links = entry.findall(f'{{{XHTML}}}link')
        assert len(links) == 8
        assert all(link.attrib['href'] in locations for link in links)
        for image in entry.findall(f'{{{IMAGE}}}image'):
            path = urlsplit(image.findtext(f'{{{IMAGE}}}loc')).path
            assert path in html
            assert (Path('app/site/static') / path.removeprefix('/static/site/')).is_file()
    assert len(entries[0].findall(f'{{{IMAGE}}}image')) == 8
    assert '<lastmod>' not in xml
