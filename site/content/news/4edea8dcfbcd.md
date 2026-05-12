+++
title = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了"
description = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了。来源：InfoQ AI。"
seo_title = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了｜AI资讯解读 - AI热榜"
seo_description = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了。来源：InfoQ AI。"
seo_keywords = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了, InfoQ AI, AI新闻, AI资讯, AI热榜"
slug = "4edea8dcfbcd"
type = "news"

[params]
id = "4edea8dcfbcd"
name = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了"
title_en = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了"
original_url = "https://www.infoq.cn/article/ikCBSErsyohVBiZ0MbxR?utm_source=rss&utm_medium=article"
source = "InfoQ AI"
published = "2026-05-07T08:00:00"
lang = "zh"
intro = "Cursor 删库毁了一家公司？资深开发者讲了大实话：把数据库交给AI的那一刻，公司就已经没了。来源：InfoQ AI。"
ai_summary = ""
summary = ""
summary_zh = ""
tags = []
list_page = 18
+++

<!-- AUTO-GENERATED: news page -->

创企 CEO 控诉 Cursor 9 秒删光其生产数据库
上周，为汽车租赁公司提供软件的初创公司 PocketOS，其创始人 Jer Crane 在 X 平台发文称，Cursor 意外删除了公司的生产数据库及备份，导致客户服务中断。

该帖迅速在社区中引发热议。

据 Crane 描述，其公司核心生产数据库在一次由 AI 自动执行的操作中被彻底删除，而整个过程仅耗时 9 秒。

PocketOS 主要为租赁企业（尤其是汽车租赁公司）提供 SaaS 系统，覆盖预订、支付、客户管理和车辆调度等关键业务流程。

部分客户已连续使用该系统超过五年，业务运行对其高度依赖。

然而，就在事故发生当天下午，一个运行在 Cursor 平台、基于 Anthropic 旗舰模型 Claude Opus 4.6 的 AI 编码代理，在执行测试环境中的常规任务时，因遭遇凭证不匹配问题，擅自决定“修复”错误——方式是删除一个 Railway 平台上的
存储卷
。

划重点：该操作通过一次 API 调用完成，没有任何确认步骤，也没有环境隔离机制，最终直接波及生产数据
。

## 🔗 原始来源

如果你要核对细节，可以再看原文：
[InfoQ AI原文链接](https://www.infoq.cn/article/ikCBSErsyohVBiZ0MbxR?utm_source=rss&utm_medium=article)

