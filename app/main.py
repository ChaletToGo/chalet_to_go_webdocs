from pathlib import Path
from contextlib import asynccontextmanager
from starlette.concurrency import run_in_threadpool

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from .revista.routes import router as revista_router
from .site.routes import router as site_router
from .site.contact import router as contact_router
from .virtual_cards.routes import router as cards_router
from .admin_pages.routes import router as admin_router
from .landing_pages.eco_villa.routes import router as eco_villa_router
from .showroom.routes import router as showroom_router
from .showroom.cache import ModelFiles, file_version
BASE_DIR = Path(__file__).resolve().parent
model_files = ModelFiles(directory=BASE_DIR/'3d')

@asynccontextmanager
async def lifespan(app):
    # Prepare transfer representations before accepting requests.
    for path in (BASE_DIR/'3d').rglob('basico_*_modelagem.glb'):
        if path.stat().st_size <= model_files.budget:
            await run_in_threadpool(model_files._compressed, str(path), file_version(path.stat()))
    yield

app = FastAPI(title="Chalet to Go", lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.mount('/static/showroom', StaticFiles(directory=BASE_DIR/'showroom'/'static'), name='showroom_static')
app.mount('/models', model_files, name='models')
app.mount('/static/admin', StaticFiles(directory=BASE_DIR/'admin_pages'/'static'), name='admin_static')
app.mount('/static/cards', StaticFiles(directory=BASE_DIR/'virtual_cards'/'static'), name='cards_static')
app.mount('/static/revista', StaticFiles(directory=BASE_DIR/'revista'/'static'), name='revista_static')
app.mount('/static/site', StaticFiles(directory=BASE_DIR/'site'/'static'), name='site_static')
app.mount('/static/eco-villa', StaticFiles(directory=BASE_DIR/'landing_pages'/'eco_villa'/'static'), name='eco_villa_static')
# Specific legacy paths must precede the shared /static mount.
app.mount('/static/css', StaticFiles(directory=BASE_DIR/'revista'/'static'/'css'), name='legacy_css')
app.mount('/static/js', StaticFiles(directory=BASE_DIR/'revista'/'static'/'js'), name='legacy_js')
app.mount('/static', StaticFiles(directory=BASE_DIR/'shared'/'static'), name='static')
app.include_router(contact_router)
app.include_router(site_router)
app.include_router(showroom_router)
app.include_router(eco_villa_router)
app.include_router(revista_router)
app.include_router(cards_router)
app.include_router(admin_router)


@app.get("/identidade", response_class=FileResponse, include_in_schema=False)
async def identity_presentation():
    return FileResponse(
        BASE_DIR/'shared'/'static'/'estudo-identidade'/'index.html',
        media_type="text/html",
        headers={"X-Robots-Tag": "noindex, nofollow"},
    )


@app.get("/healthz", include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}
