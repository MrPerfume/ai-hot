+++
title = "PyTorch Lightning AI 训练库中发现 Shai-Hulud 主题恶意软件"
description = "文章网址：https://semgrep.dev/blog/2026/malicious-dependency-in-p…"
seo_title = "PyTorch Lightning AI 训练库中发现 Shai-Hulud 主题恶意软件｜AI资讯解读 - AI热榜"
seo_description = "文章网址：https://semgrep.dev/blog/2026/malicious-dependency-in-p…"
seo_keywords = "PyTorch Lightning AI 训练库中发现 Shai-Hulud 主题恶意软件, Hacker News AI, AI新闻, AI资讯, AI热榜"
slug = "e4cdcf5db76e"
type = "news"

[params]
id = "e4cdcf5db76e"
name = "PyTorch Lightning AI 训练库中发现 Shai-Hulud 主题恶意软件"
title_en = "Shai-Hulud Themed Malware Found in the PyTorch Lightning AI Training Library"
original_url = "https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/"
source = "Hacker News AI"
published = "2026-04-30T16:09:26"
lang = "en"
intro = "文章网址：https://semgrep.dev/blog/2026/malicious-dependency-in-p…"
ai_summary = "文章网址：https://semgrep.dev/blog/2026/malicious-dependency-in-p…"
summary = "Article URL: https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/ Comments URL: https://news.ycombinator.com/item?id=47964617 Points: 331 # Comments: 111"
summary_zh = "文章网址：https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/ 评论网址：https://news.yco…"
tags = []
list_page = 11
+++

<!-- AUTO-GENERATED: news page -->

The PyPI package 'lightning', a widely-used deep learning framework, was compromised in a supply chain attack affecting versions 2.6.2 and 2.6.3 published on April 30, 2026.

Teams building image classifiers, fine-tuning LLMs, running diffusion models, or developing time-series forecasters frequently have lightning somewhere in their dependency tree.
Running pip install lightning is all that is needed to activate.

The malicious versions contain a hidden _runtime directory with obfuscated JavaScript payload that executes automatically upon module import.

The attack steals credentials, authentication tokens, environment variables, and cloud secrets, while also attempting to poison GitHub repositories.

It has Shai-Hulud themes including creating public repositories called EveryBoiWeBuildIsaWormBoi.
We believe that this attack is the work of the same threat actor behind the mini Shai-Hulud campaign.

The IOC structure is consistent with that operation: the malicious commit messages follow the same Dune-themed naming convention, with this campaign using the prefix EveryBoiWeBuildIsAWormyBoi to distinguish it from the original Mini Shai-Hulud attack.
Affected Packages
-
lightning
version
2.6.2
-
lightning

## 🔗 原始来源

如果你要核对细节，可以再看原文：
[Hacker News AI原文链接](https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/)

