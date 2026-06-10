#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SITE_CONTENT = ROOT / 'site' / 'content'
MAX_VISIBLE_NEWS_AGE_DAYS = 10
MAX_VISIBLE_MODEL_AGE_DAYS = 10

def load_json(filename):
    path = DATA / filename
    if not path.exists():
        raise FileNotFoundError(f'{filename} missing')
    return json.loads(path.read_text(encoding='utf-8'))


def records(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('items') or data.get('top_20') or []
    return []


def has_zh(text):
    return any('\u4e00' <= ch <= '\u9fff' for ch in str(text or ''))


def parse_dt(value):
    text = str(value or '').strip()
    if not text:
        return None
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(text[:19])
    except ValueError:
        try:
            dt = datetime.strptime(text[:10], '%Y-%m-%d')
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('Asia/Shanghai'))
    return dt.astimezone(ZoneInfo('Asia/Shanghai'))


def too_old(value, days):
    dt = parse_dt(value)
    if not dt:
        return True
    age_seconds = (datetime.now(ZoneInfo('Asia/Shanghai')) - dt).total_seconds()
    return age_seconds > days * 24 * 3600


def check_required_files(errors):
    for filename in ['meta.json', 'briefing.json', 'hot.json', 'news.json', 'rising.json', 'daily.json', 'models_curated.json', 'tools.json', 'agents.json']:
        if not (DATA / filename).exists():
            errors.append(f'{filename} missing')


def check_meta_and_briefing(errors):
    meta = load_json('meta.json')
    briefing = load_json('briefing.json')
    tz = ZoneInfo('Asia/Shanghai')
    last_update_raw = str(meta.get('last_update') or '').strip()
    try:
        last_update = datetime.strptime(last_update_raw, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz)
    except ValueError:
        errors.append(f'meta last_update invalid: {last_update_raw}')
        return
    age_hours = (datetime.now(tz) - last_update).total_seconds() / 3600
    if age_hours > 36:
        errors.append(f'data stale: last_update {last_update_raw}, age {age_hours:.1f}h')
    today = datetime.now(tz).strftime('%Y-%m-%d')
    if briefing.get('date') != today:
        errors.append(f'briefing date mismatch: {briefing.get("date")} != {today}')
    if not str(briefing.get('content') or '').strip():
        errors.append('briefing content empty')
    daily = load_json('daily.json')
    if daily.get('date') != today:
        errors.append(f'daily spotlight date mismatch: {daily.get("date")} != {today}')


def check_news_and_hot(errors):
    news = records(load_json('news.json'))
    hot = records(load_json('hot.json'))
    if len(news) < 5:
        errors.append(f'news too few: {len(news)}')
    if len(hot) < 3:
        errors.append(f'hot list too few: {len(hot)}')
    for idx, item in enumerate(hot[:10], 1):
        title = item.get('title_zh') or item.get('title') or ''
        summary = item.get('ai_summary') or item.get('subtitle') or item.get('description') or ''
        title_en = item.get('title_en') or item.get('title') or ''
        summary_zh = item.get('summary_zh') or item.get('ai_summary') or ''
        nid = item.get('news_id')
        if item.get('type') != 'news':
            errors.append(f'hot #{idx} not news: {title}')
        if not title:
            errors.append(f'hot #{idx} missing title')
        if not item.get('url'):
            errors.append(f'hot #{idx} missing url: {title}')
        if not summary:
            errors.append(f'hot #{idx} missing summary: {title}')
        if not title_en:
            errors.append(f'hot #{idx} missing English title: {title}')
        if not has_zh(title):
            errors.append(f'hot #{idx} missing Chinese title/label: {title}')
        if not has_zh(summary_zh):
            errors.append(f'hot #{idx} missing Chinese summary: {title}')
        if too_old(item.get('time') or item.get('detail'), MAX_VISIBLE_NEWS_AGE_DAYS):
            errors.append(f'hot #{idx} stale: {title} ({item.get("time") or item.get("detail")})')
        if not nid:
            errors.append(f'hot #{idx} missing news_id: {title}')
        elif not ((SITE_CONTENT / 'news' / f'{nid}.md').exists() or (SITE_CONTENT / 'news' / str(nid) / 'index.md').exists()):
            errors.append(f'hot #{idx} missing generated page: /news/{nid}/')


def check_dynamic_sections(errors):
    rising = records(load_json('rising.json'))
    models = records(load_json('models_curated.json'))
    tools = records(load_json('tools.json'))
    agents = records(load_json('agents.json'))
    if len(rising) < 3:
        errors.append(f'rising too few: {len(rising)}')
    if len(models) < 3:
        errors.append(f'models_curated too few: {len(models)}')
    for idx, item in enumerate(models[:5], 1):
        if too_old(item.get('freshness'), MAX_VISIBLE_MODEL_AGE_DAYS):
            errors.append(f'model #{idx} stale: {item.get("name")} ({item.get("freshness")})')
    if len(tools) < 10:
        errors.append(f'tools too few: {len(tools)}')
    if len(agents) < 5:
        errors.append(f'agents too few: {len(agents)}')

def main():
    errors=[]
    try:
        check_required_files(errors)
        check_meta_and_briefing(errors)
        check_news_and_hot(errors)
        check_dynamic_sections(errors)
    except Exception as exc:
        errors.append(str(exc))

    if errors:
        for e in errors:
            print('❌', e)
        return 1
    print('✅ quality gate passed')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
