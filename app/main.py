from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .content import PAGES
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Chalet to Go - Revista")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/healthz", include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse(url="/revista", status_code=307)


@app.get("/revista", response_class=HTMLResponse)
async def revista(request: Request):
    return templates.TemplateResponse(request, "revista.html", {"pages": PAGES})
