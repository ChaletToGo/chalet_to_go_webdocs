"""Locked TinyDB tables shared by public forms and administration."""
import json
import os
from pathlib import Path
from contextlib import contextmanager
from filelock import FileLock
from tinydb import TinyDB
from tinydb.storages import Storage

class AtomicStorage(Storage):
    """Atomic replacement; all readers/writers also hold the same process-safe lock."""
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        return json.loads(self.path.read_text('utf-8')) if self.path.exists() else None

    def write(self, data):
        temporary = self.path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)


@contextmanager
def database(table_name='qrcodes'):
    path = Path(os.getenv('ADMIN_DB_PATH', 'data/admin.json')).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + '.lock', timeout=15):
        with TinyDB(path, storage=AtomicStorage) as db:
            yield db.table(table_name)

