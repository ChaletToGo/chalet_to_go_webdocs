"""Same-origin template URLs remain valid behind TLS-terminating proxies."""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from pathlib import Path
from functools import lru_cache
from hashlib import sha256

_APP = Path(__file__).resolve().parents[1]
_STATIC = (('/static/site/', _APP/'site/static'),
           ('/static/cards/', _APP/'virtual_cards/static'),
           ('/static/revista/', _APP/'revista/static'),
           ('/static/', _APP/'shared/static'))


@lru_cache(maxsize=128)
def asset_version(path):
    if not path.endswith(('.css', '.js', '.mjs')):
        return None
    for prefix, directory in _STATIC:
        if path.startswith(prefix):
            asset = (directory / path[len(prefix):]).resolve()
            if asset.is_relative_to(directory.resolve()) and asset.is_file():
                return sha256(asset.read_bytes()).hexdigest()[:12]
            return None
    return None


def local_url(value):
    url = urlsplit(str(value))
    query = url.query
    version = asset_version(url.path)
    if version:
        query = urlencode([(key, value) for key, value in parse_qsl(query) if key != 'v'] + [('v', version)])
    return urlunsplit(('', '', url.path, query, url.fragment))
