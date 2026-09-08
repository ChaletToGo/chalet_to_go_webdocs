"""Bounded, aggregate click counts. No cookies, IPs, user IDs or referrer URLs."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from filelock import FileLock
from pydantic import BaseModel, ConfigDict

class Click(BaseModel):
    model_config = ConfigDict(extra='forbid')
    page: Literal['/', '/sobre', '/perguntas-frequentes', '/chales-para-hospedagem', '/chales/basic', '/chales/standard', '/chales/premium']
    lang: Literal['pt-BR','pt-PT','en','fr','de','it','rm']
    model: Literal['general','basic','standard','premium'] = 'general'

def enabled():
    return os.getenv('SITE_METRICS_ENABLED','false').lower()=='true'

def record(click):
    path=Path(os.getenv('SITE_METRICS_PATH','data/site-metrics.json'))
    path.parent.mkdir(parents=True,exist_ok=True)
    today=datetime.now(timezone.utc).date()
    cutoff=str(today-timedelta(days=89))
    with FileLock(str(path)+'.lock',timeout=2):
        rows=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        rows={key:value for key,value in rows.items() if key.split('|')[0]>=cutoff}
        key='|'.join((str(today),click.page,click.lang,click.model))
        rows[key]=min(rows.get(key,0)+1,10**9)
        temporary=path.with_suffix('.tmp')
        temporary.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
        temporary.replace(path)

def report():
    path=Path(os.getenv('SITE_METRICS_PATH','data/site-metrics.json'))
    rows=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    cutoff=str(datetime.now(timezone.utc).date()-timedelta(days=89))
    return [{'date':parts[0],'page':parts[1],'lang':parts[2],'model':parts[3],'whatsapp_clicks':count}
            for key,count in sorted(rows.items()) if (parts:=key.split('|'))[0]>=cutoff]
