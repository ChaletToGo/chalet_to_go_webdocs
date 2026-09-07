"""The magazine owns its editorial catalogs and render context."""
import json
from functools import lru_cache
from pathlib import Path
from ..shared.i18n import LOCALES, language_context
from .financials import budget_context, product_context

@lru_cache(maxsize=7)
def catalog(locale):
    if locale not in LOCALES:
        raise ValueError('Unsupported locale')
    return json.loads((Path(__file__).parent / 'locales' / f'{locale}.json').read_text(encoding='utf-8'))

def context_for(request):
    context = language_context(request)
    data = catalog(context['locale'])
    return {**context, 'pages':data['pages'], 'ui':data['ui'], 'finance':data['finance'],
            'budget':budget_context(), 'products':product_context()}
