"""Same-origin template URLs remain valid behind TLS-terminating proxies."""
from urllib.parse import urlsplit, urlunsplit


def local_url(value):
    url = urlsplit(str(value))
    return urlunsplit(('', '', url.path, url.query, url.fragment))
