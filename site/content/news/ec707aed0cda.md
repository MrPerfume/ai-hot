+++
title = "Anthropic 推出 Routines for Claude Code"
description = "Anthropic 推出 Routines for Claude Code。来源：InfoQ AI。"
seo_title = "Anthropic 推出 Routines for Claude Code｜AI资讯解读 - AI热榜"
seo_description = "Anthropic 推出 Routines for Claude Code。来源：InfoQ AI。"
seo_keywords = "Anthropic 推出 Routines for Claude Code, InfoQ AI, AI新闻, AI资讯, AI热榜"
slug = "ec707aed0cda"
type = "news"

[params]
id = "ec707aed0cda"
name = "Anthropic 推出 Routines for Claude Code"
title_en = "Anthropic 推出 Routines for Claude Code"
original_url = "https://www.infoq.cn/article/pqiTGU8VMOZ1fOZh8H98?utm_source=rss&utm_medium=article"
source = "InfoQ AI"
published = "2026-05-20T18:00:00"
lang = "zh"
intro = "Anthropic 推出 Routines for Claude Code。来源：InfoQ AI。"
ai_summary = ""
summary = ""
summary_zh = ""
tags = []
list_page = 13
+++

<!-- AUTO-GENERATED: news page -->

Anthropic 推出了一项名为
Routines for Claude Code
的新功能，允许开发人员配置自动化的编码工作流。

这些工作流可按计划运行、通过 API 调用触发，或响应外部事件。

该功能运行在 Claude Code 的云基础设施上，开发人员不需要在本地维护自己的 cron 任务、服务器或自动化管道。

例程由提示、存储库访问以及关联的工具或服务组成。

配置完成后，该例程可以在没有人工干预的情况下重复执行。

定时例程支持定期任务，如缺陷分类、文档变更扫描或拉取请求生成。

API 触发型例程会公开端点和身份验证令牌，从而允许部署管道、监控平台或内部工具等外部系统通过 HTTP 请求触发 Claude Code 会话。

Anthropic 还推出了
基于 webhook
的 GitHub 事件例程。

开发人员可以配置这些例程，让它们在拉取请求满足特定的条件时自动启动会话。

随后，Claude Code 可以监控拉取请求的更新、回复评论、跟踪持续集成（CI）失败，并在变更生命周期内持续运行。

该公司表示，各团队已经开始在工作流中应用这些例程，例如问题自动分诊、部署验证、警报分析、文档更新以及跨语言 SDK 同步。

其中一个示例描述了这样一种工作流：当合并
Python SDK
的拉取请求时，会自动触发一个例程，将更改移植到 Go SDK 中，并创建相应的拉取请求。

另一个示例则利用监控警报，在工程师审查事件之前，自动触发调试并生成修复草案。

## 🔗 原始来源

如果你要核对细节，可以再看原文：
[InfoQ AI原文链接](https://www.infoq.cn/article/pqiTGU8VMOZ1fOZh8H98?utm_source=rss&utm_medium=article)

