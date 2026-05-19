+++
title = "DeepSeek-V4-Flash意味着LLM指导再次变得有趣"
description = "文章网址：https://www.seangoedecke.com/steering-vectors/ 评论网址：htt…"
seo_title = "DeepSeek-V4-Flash意味着LLM指导再次变得有趣｜AI资讯解读 - AI热榜"
seo_description = "文章网址：https://www.seangoedecke.com/steering-vectors/ 评论网址：htt…"
seo_keywords = "DeepSeek-V4-Flash意味着LLM指导再次变得有趣, Hacker News AI, AI新闻, AI资讯, AI热榜"
slug = "7f1dddbf9c49"
type = "news"

[params]
id = "7f1dddbf9c49"
name = "DeepSeek-V4-Flash意味着LLM指导再次变得有趣"
title_en = "DeepSeek-V4-Flash means LLM steering is interesting again"
original_url = "https://www.seangoedecke.com/steering-vectors/"
source = "Hacker News AI"
published = "2026-05-16T14:58:16"
lang = "en"
intro = "文章网址：https://www.seangoedecke.com/steering-vectors/ 评论网址：htt…"
ai_summary = "文章网址：https://www.seangoedecke.com/steering-vectors/ 评论网址：htt…"
summary = "Article URL: https://www.seangoedecke.com/steering-vectors/ Comments URL: https://news.ycombinator.com/item?id=48160807 Points: 128 # Comments: 47"
summary_zh = "文章网址：https://www.seangoedecke.com/steering-vectors/ 评论网址：https://news.ycombinator.com/item?id=48160807 积分：128 # 评论：47"
tags = []
list_page = 11
+++

<!-- AUTO-GENERATED: news page -->

Ever since Golden Gate Claude I’ve been fascinated with “steering”: the idea that you can guide LLM outputs by directly manipulating the activations of the model mid-flight.
DeepSeek V4 Flash
I was inspired to write this post by antirez’s recent project DwarfStar 4, which is a version of llama.cpp that’s been stripped down to run only DeepSeek-V4-Flash.

What’s so special about this model? It might be what many engineers have been waiting for: a local model good enough to compete with at least the low end of frontier model agentic coding.
Since steering requires a local model, it’s now practical for many engineers to try it out for the first time.

And indeed, antirez has baked steering into DwarfStar 4 as a first-class citizen.

Right now it’s very rudimentary (basically just the toy “verbosity” example you can replicate via prompting), but the initial release was only eight days ago.

I plan to follow this project closely.
How steering works
The basic idea behind steering is extracting a concept (like “respond tersely”) from the model’s internal brain state, then reaching in during inference and boosting the numerical activations that form that concept.
One way you might do this is to feed your model the same set of a hundred prompts twice, once with the normal prompts and once with the words “respond tersely” appended.

Then measure the difference in the model’s activations1 for each prompt pair (by subtracting one activation matrix from the other).

That’s your “steering vector”.

In theory, you can go and add that to the same activation layer for any prompt and get the same effect (of the model responding tersely).
Another, more sophisticated way you might do this is to train a second model to extract “features” from your model’s activations: patterns of behavior that seem to show up together.

Then you can try to map those features back to individual concepts, and boost them in the same way.

This is more or less what Anthropic is doing with sparse autoencoders2.

It’s the same principle as the naive approach, but it lets you capture deeper patterns (at the cost of being much more expensive in time, compute and expertise).
Why steering is interesting
Steering sounds like a cheat code.

Instead of painstakingly assembling a training set that tries to push the model towards the “smart” end of the distribution in its training data, why not simply go uncover the “smart” dial in the model’s brain and turn it all the way to the right?

## 🔗 原始来源

如果你要核对细节，可以再看原文：
[Hacker News AI原文链接](https://www.seangoedecke.com/steering-vectors/)

