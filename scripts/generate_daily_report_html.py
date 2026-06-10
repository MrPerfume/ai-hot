#!/usr/bin/env python3
"""Generate a standalone daily AI report for GitHub Pages."""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

try:
    from site_config import build_site_url
except ImportError:  # pragma: no cover - used when imported as scripts.*
    from scripts.site_config import build_site_url

SH_TZ = ZoneInfo("Asia/Shanghai")


def repo_root() -> Path:
    return Path(os.environ.get("AI_HOT_ROOT", Path(__file__).resolve().parents[1])).resolve()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def items_from(data: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return []


def squash(text: Any, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def pick_title(item: dict[str, Any]) -> str:
    return squash(
        item.get("title_zh")
        or item.get("display_name")
        or item.get("title")
        or item.get("name")
        or item.get("id")
        or "未命名",
        90,
    )


def pick_summary(item: dict[str, Any]) -> str:
    return squash(
        item.get("ai_summary")
        or item.get("summary_zh")
        or item.get("subtitle")
        or item.get("description")
        or item.get("why")
        or item.get("reason")
        or item.get("use_cases")
        or "",
        180,
    )


def pick_title_en(item: dict[str, Any]) -> str:
    return squash(item.get("title_en") or item.get("title") or "", 120)


def pick_summary_en(item: dict[str, Any]) -> str:
    return squash(item.get("summary_en") or item.get("summary") or "", 220)


def internal_url_from_item(item: dict[str, Any], kind: str | None = None) -> str:
    if item.get("type") == "news" and item.get("news_id"):
        return build_site_url(f"/news/{item['news_id']}/")
    if kind == "tool" and item.get("id"):
        return build_site_url(f"/tools/{item['id']}/")
    if kind == "news" and item.get("id"):
        return build_site_url(f"/news/{item['id']}/")

    internal_url = str(item.get("internal_url") or "")
    if internal_url:
        parsed = urlparse(internal_url)
        if parsed.path:
            return build_site_url(parsed.path)
        return internal_url

    return str(item.get("url") or build_site_url("/"))


def meta_bits(item: dict[str, Any], fields: tuple[str, ...]) -> str:
    bits: list[str] = []
    for field in fields:
        value = item.get(field)
        if isinstance(value, list):
            value = " / ".join(str(x) for x in value[:3] if x)
        if value not in (None, ""):
            bits.append(str(value))
    return " · ".join(bits[:4])


def parse_report_date(meta: dict[str, Any], briefing: dict[str, Any]) -> str:
    forced = os.environ.get("AI_HOT_REPORT_DATE", "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", forced):
        return forced

    candidates = [briefing.get("date"), meta.get("last_update")]
    for value in candidates:
        text = str(value or "").strip()
        if not text:
            continue
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(text[:19], fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(SH_TZ).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return datetime.now(SH_TZ).strftime("%Y-%m-%d")


def render_item_list(
    items: list[dict[str, Any]],
    *,
    kind: str | None = None,
    limit: int = 5,
    meta_fields: tuple[str, ...] = ("source", "time", "detail", "tags"),
    bilingual: bool = False,
) -> str:
    if not items:
        return '<p class="empty">暂无可展示数据。</p>'

    rows = []
    for index, item in enumerate(items[:limit], start=1):
        title_raw = pick_title(item)
        summary_raw = pick_summary(item)
        title = escape(title_raw)
        summary = escape(summary_raw)
        href = escape(internal_url_from_item(item, kind))
        meta = escape(meta_bits(item, meta_fields))
        summary_html = f'<p class="summary">{summary}</p>' if summary else ""
        original_html = ""
        if bilingual:
            title_en = pick_title_en(item)
            summary_en = pick_summary_en(item)
            title_en_html = ""
            summary_en_html = ""
            if title_en and title_en.strip().lower() != title_raw.strip().lower():
                title_en_html = f'<p class="original"><span>English title</span>{escape(title_en)}</p>'
            if summary_en and summary_en.strip().lower() != summary_raw.strip().lower():
                summary_en_html = f'<p class="original"><span>English summary</span>{escape(summary_en)}</p>'
            original_html = title_en_html + summary_en_html
        meta_html = f'<p class="meta">{meta}</p>' if meta else ""
        rows.append(
            f"""
            <article class="item">
              <div class="rank">{index}</div>
              <div>
                <h3><a href="{href}">{title}</a></h3>
                {summary_html}
                {original_html}
                {meta_html}
              </div>
            </article>
            """.strip()
        )
    return "\n".join(rows)


def build_story_ideas(
    hot_items: list[dict[str, Any]],
    rising_items: list[dict[str, Any]],
    models: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> list[str]:
    ideas: list[str] = []
    if hot_items:
        ideas.append(f"把「{pick_title(hot_items[0])}」拆成一篇三段式：发生了什么、为什么重要、普通用户怎么跟进。")
    if len(hot_items) > 1:
        ideas.append(f"用「{pick_title(hot_items[1])}」做案例，写一篇 AI 公司商业化与估值变化观察。")
    if rising_items:
        ideas.append(f"围绕「{pick_title(rising_items[0])}」写一个新项目速读：解决什么问题、适合谁、替代品有哪些。")
    if models:
        ideas.append(f"整理「{pick_title(models[0])}」的定位：能力、成本、上下文、适合的工作流。")
    if tools:
        ideas.append(f"做一篇「{pick_title(tools[0])}」实用教程：3 个真实场景、1 个避坑点、1 个替代方案。")
    return ideas[:5]


def render_ideas(ideas: list[str]) -> str:
    if not ideas:
        return '<p class="empty">暂无选题建议。</p>'
    return "\n".join(f"<li>{escape(idea)}</li>" for idea in ideas)


def render_sources(briefing: dict[str, Any], news_items: list[dict[str, Any]]) -> str:
    sources = briefing.get("sources")
    if not isinstance(sources, dict) or not sources:
        counts: dict[str, int] = {}
        for item in news_items:
            source = str(item.get("source") or "其他")
            counts[source] = counts.get(source, 0) + 1
        sources = counts
    if not sources:
        return '<p class="empty">暂无来源统计。</p>'
    sorted_sources = sorted(sources.items(), key=lambda kv: kv[1], reverse=True)[:8]
    return "\n".join(
        f'<span class="pill">{escape(str(source))}<strong>{escape(str(count))}</strong></span>'
        for source, count in sorted_sources
    )


def render_report(
    *,
    report_date: str,
    generated_at: str,
    briefing: dict[str, Any],
    meta: dict[str, Any],
    hot_items: list[dict[str, Any]],
    rising_items: list[dict[str, Any]],
    news_items: list[dict[str, Any]],
    models: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    agents: list[dict[str, Any]],
) -> str:
    briefing_content = escape(squash(briefing.get("content"), 420))
    news_count = briefing.get("news_count") or len(news_items)
    last_update = escape(str(meta.get("last_update") or generated_at))
    ideas = build_story_ideas(hot_items, rising_items, models, tools)
    title = f"{report_date} AI 日报"

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f2;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #637083;
      --line: #d8ddd5;
      --accent: #0f766e;
      --accent-2: #b45309;
      --soft: #eef6f4;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.65;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .page {{ max-width: 1040px; margin: 0 auto; padding: 28px 18px 56px; }}
    header {{ padding: 28px 0 20px; border-bottom: 1px solid var(--line); }}
    .eyebrow {{ color: var(--accent-2); font-size: 14px; font-weight: 700; }}
    h1 {{ margin: 8px 0 10px; font-size: clamp(34px, 7vw, 68px); line-height: 1.02; letter-spacing: 0; }}
    .lead {{ max-width: 820px; margin: 0; font-size: 18px; color: #334155; }}
    .stats {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
    .stat, .pill {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 7px 10px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.72);
      border-radius: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .pill strong {{ color: var(--ink); }}
    section {{ padding: 28px 0; border-bottom: 1px solid var(--line); }}
    h2 {{ margin: 0 0 14px; font-size: 24px; letter-spacing: 0; }}
    .briefing {{
      border-left: 4px solid var(--accent);
      background: var(--soft);
      padding: 16px 18px;
      border-radius: 8px;
      font-size: 18px;
    }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .item {{
      display: grid;
      grid-template-columns: 34px minmax(0, 1fr);
      gap: 12px;
      padding: 14px 0;
      border-top: 1px solid var(--line);
    }}
    .item:first-child {{ border-top: 0; padding-top: 0; }}
    .rank {{
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: var(--ink);
      color: white;
      display: grid;
      place-items: center;
      font-size: 14px;
      font-weight: 700;
    }}
    h3 {{ margin: 0; font-size: 17px; line-height: 1.35; letter-spacing: 0; }}
    .summary {{ margin: 7px 0 0; color: #3f4d5f; }}
    .original {{
      margin: 7px 0 0;
      color: #596579;
      font-size: 14px;
      line-height: 1.55;
      border-left: 2px solid var(--line);
      padding-left: 10px;
    }}
    .original span {{
      display: inline-block;
      margin-right: 6px;
      color: var(--accent-2);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .meta {{ margin: 7px 0 0; color: var(--muted); font-size: 13px; }}
    .source-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .ideas {{ margin: 0; padding-left: 22px; }}
    .ideas li {{ margin: 9px 0; }}
    .empty {{ color: var(--muted); }}
    footer {{ padding-top: 24px; color: var(--muted); font-size: 14px; }}
    @media (max-width: 760px) {{
      .page {{ padding: 20px 14px 40px; }}
      header {{ padding-top: 18px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .panel {{ padding: 15px; }}
      .lead, .briefing {{ font-size: 16px; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <div class="eyebrow">AI Hot Daily · 每天 08:30 北京时间</div>
      <h1>{escape(title)}</h1>
      <p class="lead">{briefing_content}</p>
      <div class="stats">
        <span class="stat">新闻样本 {escape(str(news_count))}</span>
        <span class="stat">热点 {escape(str(len(hot_items)))}</span>
        <span class="stat">模型 {escape(str(len(models)))}</span>
        <span class="stat">工具 {escape(str(len(tools)))}</span>
        <span class="stat">Agent {escape(str(len(agents)))}</span>
        <span class="stat">数据更新 {last_update}</span>
      </div>
    </header>

    <section>
      <h2>今日简报</h2>
      <div class="briefing">{briefing_content}</div>
    </section>

    <section>
      <h2>热点 Top 5</h2>
      {render_item_list(hot_items, kind="news", limit=5, meta_fields=("source", "time", "detail", "tags"), bilingual=True)}
    </section>

    <section class="grid">
      <div class="panel">
        <h2>热度飙升</h2>
        {render_item_list(rising_items, limit=5, meta_fields=("type", "stars", "window_days"))}
      </div>
      <div class="panel">
        <h2>模型动态</h2>
        {render_item_list(models, limit=5, meta_fields=("provider", "badge", "freshness", "meta"))}
      </div>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>Agent 动态</h2>
        {render_item_list(agents, limit=5, meta_fields=("type", "pricing", "stars"))}
      </div>
      <div class="panel">
        <h2>工具动态</h2>
        {render_item_list(tools, kind="tool", limit=5, meta_fields=("category", "pricing", "tags"))}
      </div>
    </section>

    <section>
      <h2>可写选题</h2>
      <ol class="ideas">
        {render_ideas(ideas)}
      </ol>
    </section>

    <section>
      <h2>来源分布</h2>
      <div class="source-row">
        {render_sources(briefing, news_items)}
      </div>
    </section>

    <footer>
      生成时间：{escape(generated_at)} · 固定入口：<a href="{escape(build_site_url('/reports/latest.html'))}">latest.html</a> · 归档：<a href="{escape(build_site_url('/reports/index.html'))}">reports/index.html</a>
    </footer>
  </main>
</body>
</html>
"""


def render_index(reports_dir: Path) -> str:
    reports = sorted(
        (p for p in reports_dir.glob("*-ai-daily.html") if p.name not in {"latest.html", "index.html"}),
        reverse=True,
    )
    links = "\n".join(
        f'<li><a href="{escape(path.name)}">{escape(path.stem.replace("-ai-daily", ""))} AI 日报</a></li>'
        for path in reports
    )
    if not links:
        links = '<li class="empty">暂无归档。</li>'
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI 日报归档</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif; background: #f7f7f2; color: #1f2933; line-height: 1.65; }}
    main {{ max-width: 760px; margin: 0 auto; padding: 34px 18px 60px; }}
    h1 {{ margin: 0 0 14px; font-size: 38px; letter-spacing: 0; }}
    a {{ color: #0f766e; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    ul {{ padding-left: 22px; }}
    li {{ margin: 10px 0; }}
    .latest {{ display: inline-block; margin: 8px 0 18px; padding: 8px 12px; border: 1px solid #d8ddd5; border-radius: 8px; background: white; }}
    .empty {{ color: #637083; }}
  </style>
</head>
<body>
  <main>
    <h1>AI 日报归档</h1>
    <a class="latest" href="latest.html">打开最新日报</a>
    <ul>
      {links}
    </ul>
  </main>
</body>
</html>
"""


def generate_daily_report(root: Path | None = None) -> dict[str, Path]:
    root = (root or repo_root()).resolve()
    data_dir = root / "data"
    reports_dir = root / "site" / "static" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    briefing = load_json(data_dir / "briefing.json", {})
    hot = load_json(data_dir / "hot.json", {})
    rising = load_json(data_dir / "rising.json", {})
    news = load_json(data_dir / "news.json", [])
    models_curated = load_json(data_dir / "models_curated.json", {})
    tools_data = load_json(data_dir / "tools.json", [])
    agents_data = load_json(data_dir / "agents.json", [])
    meta = load_json(data_dir / "meta.json", {})

    hot_items = items_from(hot, "top_20", "items", "hot_list")
    rising_items = items_from(rising, "items")
    news_items = items_from(news, "items")
    models = items_from(models_curated, "items")
    tools = items_from(tools_data, "items")
    agents = items_from(agents_data, "items")

    if not briefing.get("content"):
        raise SystemExit("briefing.json 缺少 content，无法生成日报")
    if not hot_items:
        raise SystemExit("hot.json 缺少热点数据，无法生成日报")
    if not models or not tools or not agents:
        raise SystemExit("models_curated/tools/agents 数据不完整，无法生成日报")

    report_date = parse_report_date(meta, briefing)
    generated_at = datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M:%S")
    html = render_report(
        report_date=report_date,
        generated_at=generated_at,
        briefing=briefing,
        meta=meta,
        hot_items=hot_items,
        rising_items=rising_items,
        news_items=news_items,
        models=models,
        tools=tools,
        agents=agents,
    )
    html = re.sub(r"[ \t]+$", "", html, flags=re.MULTILINE)

    archive_path = reports_dir / f"{report_date}-ai-daily.html"
    latest_path = reports_dir / "latest.html"
    index_path = reports_dir / "index.html"
    archive_path.write_text(html, encoding="utf-8")
    shutil.copyfile(archive_path, latest_path)
    index_path.write_text(render_index(reports_dir), encoding="utf-8")
    return {"archive": archive_path, "latest": latest_path, "index": index_path}


def main() -> int:
    paths = generate_daily_report()
    for label, path in paths.items():
        print(f"✅ {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
