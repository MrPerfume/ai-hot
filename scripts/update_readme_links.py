#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

try:
    from site_config import build_site_url, site_url
except ImportError:  # pragma: no cover - used when imported as scripts.*
    from scripts.site_config import build_site_url, site_url

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / 'README.md'
HOT = ROOT / 'data' / 'hot.json'
BRIEFING = ROOT / 'data' / 'briefing.json'
RISING = ROOT / 'data' / 'rising.json'
META = ROOT / 'data' / 'meta.json'
DAILY = ROOT / 'data' / 'daily.json'
TOOLS = ROOT / 'data' / 'tools.json'
MODELS = ROOT / 'data' / 'models.json'
AGENTS = ROOT / 'data' / 'agents.json'
NEWS = ROOT / 'data' / 'news.json'


def _clean_hot_summary(item):
    text = (item.get('ai_summary') or item.get('subtitle') or item.get('description') or '').strip()
    text = re.sub(r'\s+', ' ', text)
    return text[:80]


def _format_hot_meta(item):
    source = item.get('source', '')
    time = item.get('time') or item.get('detail') or ''
    tags = item.get('tags') or []
    tags_text = ' / '.join(tags[:3])
    parts = [x for x in [source, time, tags_text] if x]
    return ' · '.join(parts)


def _site_link(path=''):
    return build_site_url(path)


def _json_count(path):
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        value = data.get('items') or data.get('top_20') or data.get('hot_list') or []
        return len(value)
    return 0


def _item_link(item, fallback='/'):
    if item.get('type') == 'news' and item.get('news_id'):
        return _site_link(f"/news/{item.get('news_id')}/")
    if item.get('type') == 'tool' and item.get('id'):
        return _site_link(f"/tools/{item.get('id')}/")
    internal_url = str(item.get('internal_url') or '').strip()
    if internal_url:
        parsed = urlparse(internal_url)
        if parsed.path:
            return _site_link(parsed.path)
        return internal_url
    return item.get('url') or _site_link(fallback)


def _upsert_section(text, heading, block, before_pattern=None):
    pattern = rf'{re.escape(heading)}[\s\S]*?(?=\n## |\n---|\Z)'
    if re.search(pattern, text):
        return re.sub(pattern, block.rstrip() + '\n', text, count=1)
    if before_pattern and re.search(before_pattern, text):
        return re.sub(before_pattern, '\n\n' + block.rstrip() + '\n\n' + r'\g<0>', text, count=1)
    return text.rstrip() + '\n\n' + block.rstrip() + '\n'


def update_readme_links():
    if not README.exists() or not HOT.exists():
        return '缺少 README.md 或 hot.json'

    text = README.read_text(encoding='utf-8')
    text = text.replace('https://aihot.bt199.com', site_url())
    text = text.replace('https://example.github.io/ai-hot', site_url())
    text = re.sub(r'更新频率-[^)\s]+-blue', '更新频率-每天08%3A30-blue', text)
    text = text.replace('每6小时', '每天 08:30')
    counts = {
        'tools': _json_count(TOOLS),
        'models': _json_count(MODELS),
        'agents': _json_count(AGENTS),
        'news': _json_count(NEWS),
    }
    text = re.sub(r'工具-\d+-orange', f'工具-{counts["tools"]}-orange', text)
    text = re.sub(r'模型-\d+-lightgrey', f'模型-{counts["models"]}-lightgrey', text)
    text = re.sub(r'Agent-\d+-purple', f'Agent-{counts["agents"]}-purple', text)
    text = re.sub(r'新闻-\d+-red', f'新闻-{counts["news"]}-red', text)
    text = re.sub(r'AI工具（\d+）', f'AI工具（{counts["tools"]}）', text)
    text = re.sub(r'AI模型（\d+）', f'AI模型（{counts["models"]}）', text)
    text = re.sub(r'AI Agent（\d+）', f'AI Agent（{counts["agents"]}）', text)
    text = re.sub(r'AI新闻（\d+）', f'AI新闻（{counts["news"]}）', text)
    hot = json.loads(HOT.read_text(encoding='utf-8'))
    briefing = json.loads(BRIEFING.read_text(encoding='utf-8')) if BRIEFING.exists() else {}
    rising = json.loads(RISING.read_text(encoding='utf-8')) if RISING.exists() else {}
    items = hot.get('items') or hot.get('top_20') or hot.get('hot_list') or []

    meta = json.loads(META.read_text(encoding='utf-8')) if META.exists() else {}
    last_update = meta.get('last_update') or datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    text = re.sub(r'🕐 \*\*最近更新\*\*：.*', f'🕐 **最近更新**：{last_update}', text)

    hot_lines = ['## 🔥 今日热点', '']
    for rank, item in enumerate(items[:10], start=1):
        target = _item_link(item)
        title = item.get('title_zh') or item.get('title') or item.get('name') or '未命名'
        summary_line = _clean_hot_summary(item)
        meta_line = _format_hot_meta(item)
        hot_lines.append(f'{rank}. [{title}]({target})')
        if summary_line:
            hot_lines.append(f'   - {summary_line}')
        if meta_line:
            hot_lines.append(f'   - `{meta_line}`')
        hot_lines.append('')

    hot_block = '\n'.join(hot_lines).rstrip()
    text = re.sub(r'## 🔥 今日热点[\s\S]*?(?=\n## )', hot_block + '\n\n', text, count=1)

    summary = briefing.get('content', '').strip()
    emoji = briefing.get('emoji', '⚡')
    date = briefing.get('date', '')
    news_count = briefing.get('news_count', '')
    briefing_block = f'''## 🤖 AI 简报\n\n> {emoji} {summary}\n\n`基于 {news_count} 条新闻 · {date}`\n\n👉 [打开最新 HTML 日报 →]({_site_link('/reports/latest.html')}) · [看完整 AI 新闻 →]({_site_link('/news/')})'''

    text = _upsert_section(text, '## 🤖 AI 简报', briefing_block)

    daily = json.loads(DAILY.read_text(encoding='utf-8')) if DAILY.exists() else {}
    spotlight = daily.get('spotlight') or {}
    if spotlight:
        spotlight_link = _item_link(spotlight, '/tools/')
        spotlight_block = f'''## ⭐ 今日精选

**[{spotlight.get('name', '今日精选')}]({spotlight_link})**
- {spotlight.get('description', '今天值得先看的 AI 项目')}
- `{spotlight.get('pricing', '查看详情')}`

👉 [去网站直接体验更多精选工具 →]({_site_link('/tools/')})'''
        text = _upsert_section(text, '## ⭐ 今日精选', spotlight_block)

    rising_items = rising.get('items') or []
    rising_lines = []
    for item in rising_items[:5]:
        rising_lines.append(f"- [{item.get('name','未命名')}]({item.get('url') or _site_link('/')})：{item.get('reason','最近值得关注')}")
    rising_window = rising.get('window_days', 7)
    rising_block = f"## 📈 热度飙升\n\n" + "\n".join(rising_lines) + f"\n\n👉 [去网站看完整热度飙升榜单 →]({_site_link('/')})"
    text = _upsert_section(text, '## 📈 热度飙升', rising_block)

    report_block = f'''## 🗞️ 每日 HTML 日报

- [最新日报]({_site_link('/reports/latest.html')})
- [日报归档]({_site_link('/reports/index.html')})

GitHub Actions 每天北京时间 08:30 生成一次，定时任务可能有几分钟延迟。'''
    text = _upsert_section(text, '## 🗞️ 每日 HTML 日报', report_block, before_pattern=r'\n---')
    text = re.sub(r'(\S)\n(## 🗞️ 每日 HTML 日报)', r'\1\n\n\2', text)

    README.write_text(text.rstrip() + "\n", encoding='utf-8')
    return 'README 热点链接、AI 简报与热度飙升已刷新'


if __name__ == '__main__':
    print(update_readme_links())
