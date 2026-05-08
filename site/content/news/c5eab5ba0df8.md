+++
title = "Google Chrome 在未经同意的情况下在您的设备上静默安装 4 GB AI 模型"
description = "文章网址：https://www.thatprivacyguy.com/blog/chrome-silent-nano-…"
seo_title = "Google Chrome 在未经同意的情况下在您的设备上静默安装 4 GB AI 模型｜AI资讯解读 - AI热榜"
seo_description = "文章网址：https://www.thatprivacyguy.com/blog/chrome-silent-nano-…"
seo_keywords = "Google Chrome 在未经同意的情况下在您的设备上静默安装 4 GB AI 模型, Hacker News AI, AI新闻, AI资讯, AI热榜"
slug = "c5eab5ba0df8"
type = "news"

[params]
id = "c5eab5ba0df8"
name = "Google Chrome 在未经同意的情况下在您的设备上静默安装 4 GB AI 模型"
title_en = "Google Chrome silently installs a 4 GB AI model on your device without consent"
original_url = "https://www.thatprivacyguy.com/blog/chrome-silent-nano-install/"
source = "Hacker News AI"
published = "2026-05-05T07:34:55"
lang = "en"
intro = "文章网址：https://www.thatprivacyguy.com/blog/chrome-silent-nano-…"
ai_summary = "文章网址：https://www.thatprivacyguy.com/blog/chrome-silent-nano-…"
summary = "Article URL: https://www.thatprivacyguy.com/blog/chrome-silent-nano-install/ Comments URL: https://news.ycombinator.com/item?id=48019219 Points: 455 # Comments: 423"
summary_zh = "文章网址：https://www.thatprivacyguy.com/blog/chrome-silent-nano-install/ 评论网址：https://news.ycombinator.com/item?id=48019219…"
tags = []
list_page = 17
+++

<!-- AUTO-GENERATED: news page -->

Google Chrome silently installs a 4 GB AI model on your device
Two weeks ago I wrote about Anthropic silently registering a Native Messaging bridge in seven Chromium-based browsers on every machine where Claude Desktop was installed [1].

The pattern was: install on user launch of product A, write configuration into the user's installs of products B, C, D, E, F, G, H without asking.

Reach across vendor trust boundaries.

No consent dialog.

No opt-out UI.

Re-installs itself if the user removes it manually, every time Claude Desktop is launched.
This week I discovered the same pattern, executed by Google.

Google Chrome is reaching into users' machines and writing a 4 GB on-device AI model file to disk without asking.

The file is named
weights.bin
.

It lives in
OptGuideOnDeviceModel
.

It is the weights for Gemini Nano, Google's on-device LLM.

Chrome did not ask.

Chrome does not surface it.

If the user deletes it, Chrome re-downloads it.
The legal analysis is the same one I gave for the Anthropic case.

The environmental analysis is new.

At Chrome's scale, the climate bill for one model push, paid in atmospheric CO2 by the entire planet, is between six thousand and sixty thousand tonnes of CO2-equivalent emissions, depending on how many devices receive the push.

That is the environmental cost of one company unilaterally deciding that two billion peoples' default browser will mass-distribute a 4 GB binary they did not request.
This is, in my professional opinion, a direct breach of Article 5(3) of Directive 2002/58/EC (the ePrivacy Directive) [2], a breach of the Article 5(1) GDPR principles of lawfulness, fairness, and transparency [3], a breach of Article 25 GDPR's data-protection-by-design obligation [3], and an environmental harm of a magnitude that would be a notifiable event under the Corporate Sustainability Reporting Directive (CSRD) for any in-scope undertaking [4].
What is on the disk and how it got there

## 🔗 原始来源

如果你要核对细节，可以再看原文：
[Hacker News AI原文链接](https://www.thatprivacyguy.com/blog/chrome-silent-nano-install/)

