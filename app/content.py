"""Compatibility export of the Brazilian Portuguese editorial source."""
import json
from pathlib import Path

PAGES = json.loads(
    (Path(__file__).parent / "locales" / "pt-BR.json").read_text(encoding="utf-8")
)["pages"]
