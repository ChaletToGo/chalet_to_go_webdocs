from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .revista.routes import router as revista_router
from .site.routes import router as site_router
from .virtual_cards.routes import router as cards_router
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Chalet to Go")
app.mount('/static/cards', StaticFiles(directory=BASE_DIR/'virtual_cards'/'static'), name='cards_static')
app.mount('/static/revista', StaticFiles(directory=BASE_DIR/'revista'/'static'), name='revista_static')
app.mount('/static/site', StaticFiles(directory=BASE_DIR/'site'/'static'), name='site_static')
# Specific legacy paths must precede the shared /static mount.
app.mount('/static/css', StaticFiles(directory=BASE_DIR/'revista'/'static'/'css'), name='legacy_css')
app.mount('/static/js', StaticFiles(directory=BASE_DIR/'revista'/'static'/'js'), name='legacy_js')
app.mount('/static', StaticFiles(directory=BASE_DIR/'shared'/'static'), name='static')
app.include_router(site_router)
app.include_router(revista_router)
app.include_router(cards_router)


@app.get("/healthz", include_in_schema=False)
async def healthcheck():
    return {"status": "ok!"}
