#!/usr/bin/env python3
"""Shared site URL helpers for GitHub Pages forks."""

import os

DEFAULT_SITE_URL = "https://example.github.io/ai-hot"


def site_url() -> str:
    raw = os.environ.get("AI_HOT_SITE_URL", "").strip() or DEFAULT_SITE_URL
    if raw == DEFAULT_SITE_URL:
        repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
        if "/" in repository:
            owner, name = repository.split("/", 1)
            raw = f"https://{owner}.github.io/{name}"
    return raw.rstrip("/")


def build_site_url(path: str = "") -> str:
    base = site_url()
    if not path:
        return f"{base}/"
    return f"{base}/{str(path).lstrip('/')}"
