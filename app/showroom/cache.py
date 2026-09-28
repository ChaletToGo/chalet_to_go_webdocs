"""Bounded, version-aware server cache for GLBs, with browser/CDN caching."""
from collections import OrderedDict
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs
import gzip
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.datastructures import Headers
from starlette.concurrency import run_in_threadpool


def file_version(stat):
    return f'{stat.st_mtime_ns:x}-{stat.st_size:x}'


class ModelFiles(StaticFiles):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = OrderedDict()
        self._lock = Lock()
        self._bytes = 0
        self.budget = 160 * 1024 * 1024

    def _compressed(self, path, version):
        key = (path, version)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            data = gzip.compress(Path(path).read_bytes(), compresslevel=5, mtime=0)
            while self._cache and self._bytes + len(data) > self.budget:
                _, previous = self._cache.popitem(last=False)
                self._bytes -= len(previous)
            if len(data) <= self.budget:
                self._cache[key] = data
                self._bytes += len(data)
            return data

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code not in (200, 304):
            return response
        full_path, stat = await run_in_threadpool(self.lookup_path, path)
        if not stat:
            return response
        version = file_version(stat)
        supplied = parse_qs(scope.get('query_string', b'').decode()).get('v', [''])[0]
        response.headers['Cache-Control'] = ('public, max-age=31536000, immutable' if supplied == version
                                             else 'public, max-age=0, must-revalidate')
        if not path.lower().endswith('.glb'):
            return response
        headers = Headers(scope=scope)
        response.headers['Vary'] = 'Accept-Encoding'
        # Range responses use Starlette's native byte-range implementation.
        accepts_gzip = False
        for part in headers.get('accept-encoding', '').split(','):
            encoding, *parameters = part.strip().split(';')
            if encoding != 'gzip':
                continue
            try:
                quality = next((float(p.strip()[2:]) for p in parameters if p.strip().startswith('q=')), 1.0)
                accepts_gzip = quality > 0
            except ValueError:
                pass
        if response.status_code == 304 or 'range' in headers or not accepts_gzip or stat.st_size > self.budget:
            response.headers['Content-Encoding'] = 'identity'
            return response
        body = await run_in_threadpool(self._compressed, full_path, version)
        out = dict(response.headers)
        out.update({'content-encoding': 'gzip', 'content-length': str(len(body)),
                    'content-type': 'model/gltf-binary'})
        # Weak validators describe the same GLB across transfer encodings.
        out['etag'] = 'W/' + out['etag'].removeprefix('W/')
        return Response(b'' if scope['method'] == 'HEAD' else body, headers=out)
