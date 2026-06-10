import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.generate_daily_report_html import generate_daily_report


class GenerateDailyReportHtmlTests(unittest.TestCase):
    def test_generates_archive_latest_and_index_with_escaped_content(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = root / "data"
            data.mkdir()

            (data / "briefing.json").write_text(json.dumps({
                "date": "2026-06-10",
                "content": "今天 <AI> 的主线是从模型能力走向落地系统。",
                "news_count": 2,
                "sources": {"TechCrunch AI": 1, "量子位": 1},
            }, ensure_ascii=False), encoding="utf-8")
            (data / "hot.json").write_text(json.dumps({
                "top_20": [{
                    "title_zh": "测试热点 <unsafe>",
                    "type": "news",
                    "news_id": "abc123",
                    "source": "TechCrunch AI",
                    "ai_summary": "摘要内容",
                }]
            }, ensure_ascii=False), encoding="utf-8")
            (data / "rising.json").write_text(json.dumps({
                "items": [{"name": "Rising Tool", "url": "https://example.com", "reason": "最近值得关注"}]
            }, ensure_ascii=False), encoding="utf-8")
            (data / "news.json").write_text(json.dumps([
                {"id": "abc123", "source": "TechCrunch AI", "title_zh": "测试新闻"}
            ], ensure_ascii=False), encoding="utf-8")
            (data / "models_curated.json").write_text(json.dumps({
                "items": [{"name": "Model X", "provider": "OpenAI", "why": "适合复杂任务"}]
            }, ensure_ascii=False), encoding="utf-8")
            (data / "tools.json").write_text(json.dumps([
                {"id": "cursor", "name": "Cursor", "description": "AI 编程工具"}
            ], ensure_ascii=False), encoding="utf-8")
            (data / "agents.json").write_text(json.dumps([
                {"id": "agent", "name": "Agent X", "description": "自动化工作流"}
            ], ensure_ascii=False), encoding="utf-8")
            (data / "meta.json").write_text(json.dumps({
                "last_update": "2026-06-10 08:31:00"
            }, ensure_ascii=False), encoding="utf-8")

            with patch.dict("os.environ", {
                "AI_HOT_REPORT_DATE": "2026-06-10",
                "AI_HOT_SITE_URL": "https://user.github.io/ai-hot/",
            }):
                paths = generate_daily_report(root)

            latest = paths["latest"].read_text(encoding="utf-8")
            index = paths["index"].read_text(encoding="utf-8")

        self.assertTrue(paths["archive"].name.endswith("2026-06-10-ai-daily.html"))
        self.assertIn("2026-06-10 AI 日报", latest)
        self.assertIn("&lt;AI&gt;", latest)
        self.assertIn("测试热点 &lt;unsafe&gt;", latest)
        self.assertIn("https://user.github.io/ai-hot/news/abc123/", latest)
        self.assertIn("热点 Top 5", latest)
        self.assertIn("可写选题", latest)
        self.assertIn("2026-06-10 AI 日报", index)


if __name__ == "__main__":
    unittest.main()
