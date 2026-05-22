+++
title = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整"
description = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整。来源：InfoQ AI。"
seo_title = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整｜AI资讯解读 - AI热榜"
seo_description = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整。来源：InfoQ AI。"
seo_keywords = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整, InfoQ AI, AI新闻, AI资讯, AI热榜"
slug = "eea702ad60ee"
type = "news"

[params]
id = "eea702ad60ee"
name = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整"
title_en = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整"
original_url = "https://www.infoq.cn/article/yxuH0IZNUvwPGdAEKCFX?utm_source=rss&utm_medium=article"
source = "InfoQ AI"
published = "2026-05-19T16:07:00"
lang = "zh"
intro = "Anthropic发布工程事故报告，说明六周来Claude Code质量下降源于三项产品调整。来源：InfoQ AI。"
ai_summary = ""
summary = ""
summary_zh = ""
tags = []
list_page = 22
+++

<!-- AUTO-GENERATED: news page -->

Anthropic 发布了一份
工程事故复盘报告
，针对六周以来用户反馈的 Claude Code 相关投诉作出情况说明。

用户反馈的症状差异极大，具体取决于他们使用 Claude Code 的时段和功能。

究其原因，2026 年 3 月至 4 月期间，三个互不相关的产品层变更陆续上线，每个变更都按照各自的时间表影响了不同的流量切片。

API 接口与底层模型权重均未受到影响。

截至 4 月 20 日（v2.1.116），这三个问题已全部修复，Anthropic 也已为所有订阅用户重置了使用额度。

第一个是推理强度降级。

3 月 4 日，Anthropic 将 Claude Code 的默认推理强度从高等级调整为中等等级，以此解决长时间思考期间界面卡顿的问题。

官方坦言这是一次“错误的权衡”。

不少用户反馈 Claude Code 智能表现有所下降，即便界面优化后强度设置选项更加醒目，但多数用户依旧沿用中等默认档位。

这个改动已于 4 月 7 日回滚，目前所有模型默认启用高等级或极高等级推理强度。

第二个是一个缓存漏洞，该问题会逐步清空模型自身的推理过程。

3 月 26 日，Anthropic 上线了一项优化功能，用于清理闲置时长超一小时的思考片段，这类会话原本就会出现完全缓存未命中的情况。

但一处漏洞导致清除操作在会话剩余时间内的每一轮都触发，而非仅触发一次。

Claude 虽能正常继续运行，却会逐渐遗忘自身选用当前处理方式的缘由。

Claude Code 团队的 Boris Cherny 在
Hacker News
上解释，极端情况下，若用户上下文包含 90 万词元且会话闲置一小时，发送下一条消息时会出现完全缓存未命中，消耗大量速率限制额度，对 Pro 用户影响尤为明显。

他们为降低这一成本而推出的修复方案正是引入该漏洞的直接原因。

该问题已于 4 月 10 日修复。

（该缓存漏洞会在每轮交互后清除 Claude 的推理历史，而非仅清除一次。

来源：

## 🔗 原始来源

如果你要核对细节，可以再看原文：
[InfoQ AI原文链接](https://www.infoq.cn/article/yxuH0IZNUvwPGdAEKCFX?utm_source=rss&utm_medium=article)

