#!/usr/bin/env python3
"""Lightweight daily collector for AI Hot.

This script intentionally avoids the original heavy enrichment chain. It uses
public RSS/API sources, deterministic ranking, and local page generators so the
fork can keep producing a daily report even when upstream data stops moving.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import feedparser
import requests

from enrich_hot_data import enrich_hot_data
from daily_spotlight import select_daily_spotlight
from generate_daily_report_html import generate_daily_report
from generate_news_pages import generate_news_pages
from generate_sitemap import generate_sitemap
from generate_tool_pages import generate_tool_pages
from site_config import build_site_url
from update_readme_links import update_readme_links

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE_DATA = ROOT / "site" / "data"
SH_TZ = ZoneInfo("Asia/Shanghai")
USER_AGENT = "MrPerfume-ai-hot-daily/1.0 (+https://github.com/MrPerfume/ai-hot)"
NEWS_LOOKBACK_DAYS = int(os.environ.get("AI_HOT_NEWS_LOOKBACK_DAYS", "10"))
MODEL_LOOKBACK_DAYS = int(os.environ.get("AI_HOT_MODEL_LOOKBACK_DAYS", "10"))
TRANSLATE_ENABLED = os.environ.get("AI_HOT_TRANSLATE", "1").strip() != "0"
TRANSLATE_LIMIT = int(os.environ.get("AI_HOT_TRANSLATE_LIMIT", "20"))
TRANSLATE_SLEEP_SECONDS = float(os.environ.get("AI_HOT_TRANSLATE_SLEEP_SECONDS", "0.2"))
TRANSLATION_CACHE = DATA / "translation_cache.json"

RSS_SOURCES = [
    {"name": "OpenAI News", "url": "https://openai.com/news/rss.xml", "lang": "en", "priority": 10},
    {"name": "Google AI", "url": "https://blog.google/technology/ai/rss/", "lang": "en", "priority": 9},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "lang": "en", "priority": 8},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "lang": "en", "priority": 8},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "lang": "en", "priority": 7},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "lang": "en", "priority": 7},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "lang": "en", "priority": 6},
    {"name": "量子位", "url": "https://www.qbitai.com/feed", "lang": "zh", "priority": 8},
]

AI_TERMS = (
    "ai",
    "artificial intelligence",
    "agent",
    "llm",
    "model",
    "openai",
    "anthropic",
    "claude",
    "chatgpt",
    "gpt",
    "gemini",
    "deepseek",
    "qwen",
    "llama",
    "hugging face",
    "sora",
    "人工智能",
    "大模型",
    "智能体",
    "模型",
    "算力",
    "机器人",
)

BAD_MODEL_TERMS = (
    "nsfw",
    "uncensored",
    "sloppy",
    "blowjob",
    "porn",
    "hentai",
    "nude",
    "sex",
    "abliterated",
    "abliterate",
    "obliterated",
)

TRUSTED_MODEL_AUTHORS = {
    "openai",
    "google",
    "meta-llama",
    "mistralai",
    "qwen",
    "deepseek-ai",
    "nvidia",
    "coherelabs",
    "liquidai",
    "xiaomimimo",
    "zai-org",
    "microsoft",
    "black-forest-labs",
}

THEME_RULES = [
    ("模型能力", ("model", "gpt", "claude", "gemini", "llm", "qwen", "deepseek", "llama", "大模型", "模型")),
    ("Agent 和自动化", ("agent", "workflow", "automation", "tool use", "智能体", "自动化")),
    ("产品与应用", ("app", "product", "assistant", "search", "browser", "产品", "应用", "助手", "搜索")),
    ("开源生态", ("open source", "github", "hugging face", "repo", "开源")),
    ("基础设施与算力", ("chip", "gpu", "inference", "data center", "infrastructure", "芯片", "算力", "推理")),
    ("安全与治理", ("safety", "security", "policy", "copyright", "regulation", "安全", "监管", "版权")),
]


def now_sh() -> datetime:
    return datetime.now(SH_TZ)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(value: Any, limit: int = 500) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    text = re.sub(r"\s+", " ", text)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&nbsp;", " ")
        .strip()
    )
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "…"
    return text


def has_zh(text: Any) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in str(text or ""))


def stable_id(url: str, prefix: str = "") -> str:
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}{digest}" if prefix else digest


def parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            try:
                dt = parsedate_to_datetime(text)
            except Exception:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(SH_TZ)


def published_from_entry(entry: Any) -> str:
    for key in ("published", "updated", "created"):
        dt = parse_dt(entry.get(key))
        if dt:
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
    return now_sh().strftime("%Y-%m-%dT%H:%M:%S")


def is_recent(value: Any, days: int) -> bool:
    dt = parse_dt(value)
    if not dt:
        return False
    return dt >= now_sh() - timedelta(days=days)


def local_date_label(value: Any) -> str:
    dt = parse_dt(value)
    if dt:
        return dt.strftime("%Y-%m-%d")
    return str(value or "")[:10]


def term_in_text(term: str, text: str) -> bool:
    if len(term) <= 3 and term.isascii():
        return re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text) is not None
    return term in text


def is_ai_related(title: str, summary: str) -> bool:
    blob = f"{title} {summary}".lower()
    return any(term_in_text(term, blob) for term in AI_TERMS)


def title_for_reader(title: str, source: str, lang: str) -> str:
    title = clean_text(title, 120)
    if lang == "zh" or has_zh(title):
        return title
    return title


def fallback_zh_title(title: str) -> str:
    return clean_text(f"AI 动态：{title}", 120)


def fallback_zh_summary(title: str, source: str) -> str:
    return clean_text(f"中文速读：这条来自 {source} 的 AI 动态关注「{title}」。建议结合英文原文查看具体细节。", 220)


def summary_for_reader(title: str, summary: str, source: str, lang: str) -> str:
    summary = clean_text(summary, 220)
    if lang == "zh" or has_zh(summary):
        return summary or title
    return fallback_zh_summary(title, source)


def translation_key(text: str) -> str:
    return hashlib.sha1(f"en|zh-CN|{text}".encode("utf-8")).hexdigest()


def translate_en_to_zh(text: str, cache: dict[str, str]) -> str:
    text = clean_text(text, 420)
    if not text:
        return ""
    if has_zh(text):
        return text
    if not TRANSLATE_ENABLED:
        return ""
    key = translation_key(text)
    if cache.get(key):
        return cache[key]
    try:
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": "en|zh-CN"},
            headers={"User-Agent": USER_AGENT},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        translated = clean_text((data.get("responseData") or {}).get("translatedText"), 420)
        if translated and has_zh(translated) and translated.lower() != text.lower():
            cache[key] = translated
            if TRANSLATE_SLEEP_SECONDS > 0:
                time.sleep(TRANSLATE_SLEEP_SECONDS)
            return translated
    except Exception as exc:
        print(f"  ⚠️ translate failed: {exc}")
    return ""


def bilingualize_news(news: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    cache = read_json(TRANSLATION_CACHE, {})
    if not isinstance(cache, dict):
        cache = {}
    translated_count = 0
    changed_cache = False

    for index, item in enumerate(news):
        title = clean_text(item.get("title"), 160)
        summary = clean_text(item.get("summary"), 260)
        source = str(item.get("source") or "公开来源")
        lang = str(item.get("lang") or "").lower()
        item["title_en"] = title
        item["summary_en"] = summary

        if lang == "zh" or has_zh(title):
            item["title_zh"] = item.get("title_zh") or title
        elif index < TRANSLATE_LIMIT:
            before = len(cache)
            translated = translate_en_to_zh(title, cache)
            changed_cache = changed_cache or len(cache) != before
            if translated:
                item["title_zh"] = translated
                translated_count += 1
            else:
                item["title_zh"] = fallback_zh_title(title)
        else:
            item["title_zh"] = fallback_zh_title(title)

        if lang == "zh" or has_zh(summary):
            item["summary_zh"] = item.get("summary_zh") or summary or item["title_zh"]
        elif index < TRANSLATE_LIMIT and summary:
            before = len(cache)
            translated = translate_en_to_zh(summary, cache)
            changed_cache = changed_cache or len(cache) != before
            if translated:
                item["summary_zh"] = translated
                translated_count += 1
            else:
                item["summary_zh"] = fallback_zh_summary(title, source)
        else:
            item["summary_zh"] = fallback_zh_summary(title, source)

        item["ai_summary"] = item["summary_zh"]
        item["bilingual"] = True

    if changed_cache:
        write_json(TRANSLATION_CACHE, cache)
    return news, translated_count


def source_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        source = item.get("source") or "其他"
        counts[source] = counts.get(source, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def request_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
    response.raise_for_status()
    return response.json()


def collect_rss_news() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"], request_headers={"User-Agent": USER_AGENT})
            for entry in feed.entries[:18]:
                title = clean_text(entry.get("title"), 160)
                url = str(entry.get("link") or "").strip()
                summary = clean_text(entry.get("summary") or entry.get("description"), 260)
                if not title or not url or not is_ai_related(title, summary):
                    continue
                published = published_from_entry(entry)
                if not is_recent(published, NEWS_LOOKBACK_DAYS):
                    continue
                item_id = stable_id(url)
                title_zh = title_for_reader(title, source["name"], source["lang"])
                summary_zh = summary_for_reader(title, summary, source["name"], source["lang"])
                items.append({
                    "id": item_id,
                    "title": title,
                    "title_en": title,
                    "title_zh": title_zh,
                    "url": url,
                    "source": source["name"],
                    "lang": source["lang"],
                    "priority": source["priority"],
                    "published": published,
                    "summary": summary,
                    "summary_en": summary,
                    "summary_zh": summary_zh,
                    "ai_summary": summary_zh,
                    "collected_at": now_sh().isoformat(timespec="seconds"),
                })
        except Exception as exc:
            print(f"  ⚠️ RSS {source['name']} failed: {exc}")
    return items


def collect_hn_news() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    queries = ["AI", "LLM", "OpenAI", "Claude", "AI agent"]
    since_ts = int((now_sh() - timedelta(days=NEWS_LOOKBACK_DAYS)).timestamp())
    for query in queries:
        try:
            data = request_json(
                "https://hn.algolia.com/api/v1/search_by_date",
                {"query": query, "tags": "story", "hitsPerPage": 12, "numericFilters": f"created_at_i>{since_ts}"},
            )
        except Exception as exc:
            print(f"  ⚠️ HN {query} failed: {exc}")
            continue
        for hit in data.get("hits") or []:
            title = clean_text(hit.get("title"), 160)
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if not title or not url or not is_ai_related(title, ""):
                continue
            points = int(hit.get("points") or 0)
            if points < 20:
                continue
            summary = f"Hacker News 讨论热度 {points} 分，适合跟进技术社区对这条 AI 动态的反馈。"
            published = published_from_entry({"published": hit.get("created_at")})
            if not is_recent(published, NEWS_LOOKBACK_DAYS):
                continue
            items.append({
                "id": f"hn-{hit.get('objectID')}",
                "title": title,
                "title_en": title,
                "title_zh": title,
                "url": url,
                "source": "Hacker News",
                "lang": "en",
                "priority": min(8, 3 + points // 80),
                "published": published,
                "summary": summary,
                "summary_en": summary,
                "summary_zh": summary,
                "ai_summary": summary,
                "points": points,
                "collected_at": now_sh().isoformat(timespec="seconds"),
            })
    return items


def dedupe_news(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for item in items:
        key = re.sub(r"\W+", "", (item.get("url") or item.get("title") or "").lower()).strip()
        if not key or not is_recent(item.get("published"), NEWS_LOOKBACK_DAYS):
            continue
        old = seen.get(key)
        if not old or int(item.get("priority") or 0) > int(old.get("priority") or 0):
            seen[key] = item

    def score(item: dict[str, Any]) -> tuple[float, str]:
        dt = parse_dt(item.get("published")) or now_sh()
        age_hours = max((now_sh() - dt).total_seconds() / 3600, 0)
        recency = max(0, 96 - age_hours)
        return (recency + float(item.get("priority") or 0) * 12 + float(item.get("points") or 0) / 8, item.get("published") or "")

    ranked = sorted(seen.values(), key=score, reverse=True)
    return ranked[:80]


def hot_from_news(news: list[dict[str, Any]]) -> dict[str, Any]:
    hot_items = []
    for item in news[:10]:
        news_id = item.get("id")
        hot_items.append({
            "title": item.get("title"),
            "title_en": item.get("title_en") or item.get("title"),
            "name": item.get("title_zh") or item.get("title"),
            "title_zh": item.get("title_zh") or item.get("title"),
            "url": item.get("url"),
            "type": "news",
            "source": item.get("source"),
            "score": int(item.get("priority") or 1),
            "detail": str(item.get("published") or "")[:10],
            "time": str(item.get("published") or "")[:10],
            "description": item.get("ai_summary") or item.get("summary_zh") or item.get("summary"),
            "subtitle": item.get("ai_summary") or item.get("summary_zh") or item.get("summary"),
            "ai_summary": item.get("ai_summary") or item.get("summary_zh") or item.get("summary"),
            "summary": item.get("summary"),
            "summary_en": item.get("summary_en") or item.get("summary"),
            "summary_zh": item.get("summary_zh") or item.get("ai_summary"),
            "category": "资讯",
            "news_id": news_id,
            "internal_url": build_site_url(f"/news/{news_id}/") if news_id else "",
            "type_label": "📰 新闻",
        })
    return {
        "updated_at": now_sh().isoformat(timespec="seconds"),
        "total": len(hot_items),
        "hot_list": hot_items,
        "top_20": hot_items,
        "items": hot_items,
        "type_stats": {"news": len(hot_items), "tool": 0, "project": 0, "model": 0},
    }


def detect_themes(news: list[dict[str, Any]]) -> list[str]:
    counts: dict[str, int] = {}
    for item in news[:30]:
        blob = f"{item.get('title', '')} {item.get('summary', '')} {item.get('summary_zh', '')}".lower()
        for theme, terms in THEME_RULES:
            if any(term in blob for term in terms):
                counts[theme] = counts.get(theme, 0) + 1
    return [theme for theme, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:3]]


def build_briefing(news: list[dict[str, Any]]) -> dict[str, Any]:
    today = now_sh().strftime("%Y-%m-%d")
    themes = detect_themes(news)
    top_titles = [item.get("title_zh") or item.get("title") for item in news[:3]]
    theme_text = "、".join(themes) if themes else "模型、产品和开源生态"
    title_text = "；".join(t for t in top_titles if t)
    content = f"今天 AI 动态主要集中在{theme_text}。值得先看：{title_text}。"
    return {
        "date": today,
        "content": clean_text(content, 420),
        "news_count": len(news),
        "sources": source_counts(news),
        "emoji": "⚡",
    }


def collect_github_projects() -> list[dict[str, Any]]:
    since = (now_sh() - timedelta(days=30)).strftime("%Y-%m-%d")
    queries = [
        f"topic:artificial-intelligence pushed:>{since} stars:>100",
        f"ai agent pushed:>{since} stars:>100",
        f"llm pushed:>{since} stars:>100",
    ]
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for query in queries:
        try:
            data = request_json(
                "https://api.github.com/search/repositories",
                {"q": query, "sort": "stars", "order": "desc", "per_page": 15},
            )
        except Exception as exc:
            print(f"  ⚠️ GitHub search failed: {exc}")
            continue
        for repo in data.get("items") or []:
            full_name = repo.get("full_name")
            if not full_name or full_name in seen:
                continue
            seen.add(full_name)
            items.append({
                "id": f"github-{repo.get('id')}",
                "name": full_name,
                "display_name": repo.get("name") or full_name,
                "url": repo.get("html_url"),
                "description": clean_text(repo.get("description"), 180),
                "stars": repo.get("stargazers_count") or 0,
                "language": repo.get("language") or "",
                "created_at": repo.get("created_at") or "",
                "updated_at": repo.get("updated_at") or "",
                "collected_at": now_sh().isoformat(timespec="seconds"),
            })
    return sorted(items, key=lambda x: int(x.get("stars") or 0), reverse=True)[:60]


def collect_hf_models() -> list[dict[str, Any]]:
    endpoints = [
        ("newest", "https://huggingface.co/api/models", {"sort": "createdAt", "direction": "-1", "limit": 20}),
        ("trending", "https://huggingface.co/api/models", {"sort": "likes7d", "limit": 30}),
        ("text-generation", "https://huggingface.co/api/models", {"pipeline_tag": "text-generation", "sort": "likes7d", "limit": 20}),
    ]
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source, url, params in endpoints:
        try:
            data = request_json(url, params)
        except Exception as exc:
            print(f"  ⚠️ Hugging Face {source} failed: {exc}")
            continue
        for model in data or []:
            model_id = model.get("id")
            if not model_id or model_id in seen:
                continue
            tags = model.get("tags") or []
            author = model_id.split("/")[0] if "/" in model_id else ""
            likes = int(model.get("likes") or 0)
            downloads = int(model.get("downloads") or 0)
            created_at = model.get("createdAt") or ""
            blob = f"{model_id} {' '.join(str(tag) for tag in tags)}".lower()
            if any(term in blob for term in BAD_MODEL_TERMS):
                continue
            if not is_recent(created_at, MODEL_LOOKBACK_DAYS):
                continue
            if author.lower() not in TRUSTED_MODEL_AUTHORS and likes < 50 and downloads < 500:
                continue
            seen.add(model_id)
            items.append({
                "id": f"hf-{model_id.replace('/', '--')}",
                "name": model_id,
                "display_name": model_id.split("/")[-1],
                "url": f"https://huggingface.co/{model_id}",
                "author": author,
                "pipeline_tag": model.get("pipeline_tag") or "",
                "likes": likes,
                "downloads": downloads,
                "tags": tags,
                "created_at": created_at,
                "source": f"Hugging Face {source}",
                "collected_at": now_sh().isoformat(timespec="seconds"),
            })
    def model_score(item: dict[str, Any]) -> tuple[float, int, int]:
        dt = parse_dt(item.get("created_at")) or now_sh()
        age_hours = max((now_sh() - dt).total_seconds() / 3600, 0)
        recency = max(0, MODEL_LOOKBACK_DAYS * 24 - age_hours)
        likes = int(item.get("likes") or 0)
        downloads = int(item.get("downloads") or 0)
        return (recency * 8 + likes * 2 + math.sqrt(downloads), likes, downloads)

    return sorted(items, key=model_score, reverse=True)[:80]


def models_curated_from_hf(models: list[dict[str, Any]]) -> dict[str, Any]:
    items = []
    for model in models[:18]:
        items.append({
            "category": "watch",
            "source": "Hugging Face",
            "name": model.get("display_name") or model.get("name"),
            "provider": model.get("author") or "Hugging Face",
            "url": model.get("url"),
            "freshness": local_date_label(model.get("created_at")),
            "badge": "今日关注",
            "why": f"{model.get('source', 'Hugging Face')} 收录，likes {model.get('likes', 0)} / downloads {model.get('downloads', 0)}",
            "meta": model.get("pipeline_tag") or "model",
            "tags": (model.get("tags") or [])[:5],
            "icon_url": "https://huggingface.co/front/assets/huggingface_logo-noborder.svg",
        })
    return {
        "updated_at": now_sh().isoformat(timespec="seconds"),
        "total": len(items),
        "categories": [{"id": "watch", "name": "今日关注", "description": "轻量采集链从 Hugging Face 选出的模型动态"}],
        "items": items,
    }


def rising_from(projects: list[dict[str, Any]], models: list[dict[str, Any]]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for project in projects[:8]:
        candidates.append({
            "id": project.get("id"),
            "name": project.get("display_name") or project.get("name"),
            "url": project.get("url"),
            "description": project.get("description") or "近期活跃的 AI 开源项目",
            "type": "project",
            "stars": project.get("stars") or 0,
            "score": int(project.get("stars") or 0),
            "window_days": 30,
            "reason": project.get("description") or "近期活跃的 AI 开源项目",
        })
    for model in models[:8]:
        likes = int(model.get("likes") or 0)
        downloads = int(model.get("downloads") or 0)
        candidates.append({
            "id": model.get("id"),
            "name": model.get("display_name") or model.get("name"),
            "url": model.get("url"),
            "description": model.get("pipeline_tag") or "Hugging Face 模型动态",
            "type": "model",
            "stars": likes,
            "score": likes * 3 + int(math.sqrt(downloads)),
            "window_days": 30,
            "reason": f"Hugging Face 模型动态，likes {likes} / downloads {downloads}",
        })
    candidates = sorted(candidates, key=lambda item: int(item.get("score") or 0), reverse=True)
    return {
        "updated_at": now_sh().isoformat(timespec="seconds"),
        "window_days": 30,
        "candidate_count": len(candidates),
        "items": candidates[:8],
    }


def sync_site_data() -> str:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in DATA.glob("*.json"):
        if path.name == "translation_cache.json":
            continue
        shutil.copy2(path, SITE_DATA / path.name)
        count += 1
    return f"同步 {count} 个 JSON 到 site/data"


def summarize_result(value: Any) -> str:
    if isinstance(value, list):
        return f"{len(value)} 条"
    if isinstance(value, dict):
        if {"archive", "latest", "index"}.issubset(value.keys()):
            return ", ".join(f"{key}={Path(path).name}" for key, path in value.items())
        if "items" in value:
            return f"{len(value.get('items') or [])} 条"
        return f"{len(value)} 项"
    return str(value)


def write_meta(results: dict[str, str]) -> None:
    write_json(DATA / "meta.json", {
        "last_update": now_sh().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "light-1.0",
        "collector": "light_daily_aggregate.py",
        "results": results,
    })


def run_step(results: dict[str, str], label: str, func) -> Any:
    print(f"  {label}...")
    try:
        value = func()
        summary = summarize_result(value)
        results[label] = f"✅ {summary}"
        print(f"    → {summary}")
        return value
    except Exception as exc:
        results[label] = f"❌ {exc}"
        print(f"    → ❌ {exc}")
        return None


def main() -> int:
    print(f"🚀 AI热榜轻量采集 - {now_sh().strftime('%Y-%m-%d %H:%M:%S')}")
    results: dict[str, str] = {}

    rss_news = run_step(results, "RSS 新闻", collect_rss_news) or []
    hn_news = run_step(results, "HN 新闻", collect_hn_news) or []
    news = dedupe_news(rss_news + hn_news)
    if len(news) < 5:
        raise SystemExit(f"采集到的新闻过少：{len(news)}")
    news, translated_count = bilingualize_news(news)
    results["双语增强"] = f"✅ {translated_count} 段翻译"
    write_json(DATA / "news.json", news)
    results["写入新闻"] = f"✅ {len(news)} 条"

    hot = hot_from_news(news)
    write_json(DATA / "hot.json", hot)
    results["生成热点"] = f"✅ {len(hot.get('top_20') or [])} 条"

    briefing = build_briefing(news)
    write_json(DATA / "briefing.json", briefing)
    results["生成简报"] = f"✅ {briefing['date']}"

    projects = run_step(results, "GitHub 项目", collect_github_projects) or []
    if projects:
        write_json(DATA / "projects.json", projects)

    models = run_step(results, "Hugging Face 模型", collect_hf_models) or []
    if models:
        write_json(DATA / "models.json", models)
        write_json(DATA / "models_curated.json", models_curated_from_hf(models))

    rising = rising_from(projects, models)
    write_json(DATA / "rising.json", rising)
    results["生成飙升"] = f"✅ {len(rising.get('items') or [])} 条"
    run_step(results, "每日精选", select_daily_spotlight)

    write_meta(results)
    run_step(results, "生成新闻页", generate_news_pages)
    run_step(results, "生成工具页", generate_tool_pages)
    run_step(results, "热点内链补全", enrich_hot_data)
    run_step(results, "同步站点数据", sync_site_data)
    run_step(results, "生成 Sitemap", generate_sitemap)
    write_meta(results)
    run_step(results, "更新 README", update_readme_links)
    write_meta(results)
    run_step(results, "生成 HTML 日报", generate_daily_report)

    failures = [value for value in results.values() if value.startswith("❌")]
    print(f"\n📊 完成：{len(results) - len(failures)} 成功 / {len(failures)} 失败")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
