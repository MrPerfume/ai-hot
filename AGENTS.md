# AGENTS.md - ai-hot-daily

> 本文件只记录本项目特有规则。长期个人偏好放在 `~/.codex/AGENTS.md`。

## 项目定位

- 项目用途：基于 `laolaoshiren/ai-hot` fork，每天用轻量采集链生成 AI 热点 HTML 日报并发布到 GitHub Pages。
- 目标用户：个人每日浏览 AI 新闻、模型、工具和 Agent 动态。
- 当前阶段：轻量自动化日报，不接入 SignalForge。
- 成功标准：GitHub Actions 每天北京时间 08:30 生成并发布 `/reports/latest.html` 和每日归档。
- 不做的事情：暂不接邮件、微信、飞书、SignalForge，不绑定自定义域名。

## 关键约束

- GitHub Pages 使用默认域名：`https://<owner>.github.io/<repo>/`。
- 不恢复根目录 `CNAME`，不写死 `aihot.bt199.com` 作为站点发布域名。
- 日报页面放在 `site/static/reports/`，必须是可独立访问的自包含 HTML。
- 自动化流程先跑数据聚合、测试和质量门禁，再生成日报。
- 每日任务使用 `scripts/light_daily_aggregate.py`，不再依赖上游仓库或源站是否更新。
- 轻量链只抓公开 RSS/API，不使用登录态、Cookie 或私有账号。
- 定时任务是 GitHub Actions cron，`30 0 * * *` 对应北京时间 08:30；允许平台有几分钟延迟。

## 常用命令

```bash
python -m unittest discover -s tests -p 'test_*.py'
python scripts/light_daily_aggregate.py
python scripts/generate_daily_report_html.py
python scripts/quality_gate.py
```

## 常用验证

- `python -m unittest discover -s tests -p 'test_*.py'`
- `python -m py_compile scripts/generate_daily_report_html.py scripts/site_config.py scripts/generate_sitemap.py`
- `git diff --check`
- GitHub 上手动触发 `Daily AI Data Aggregation`
- Pages 发布后检查 `/reports/latest.html` 和 `/reports/index.html`

## 数据与发布

- `data/*.json` 是日报的数据源；本地旧数据可能导致 `quality_gate.py` 报 stale。
- workflow 中 `AI_HOT_SITE_URL` 会自动使用当前 fork 的 GitHub Pages 地址。
- `deploy.yml` 会在发布前重新生成 sitemap、robots 和日报，避免静态产物残留旧域名。

## Git 规则

- 提交信息使用中文。
- 提交前查看 `git status --short`。
- 只暂存本次日报自动化相关文件。
