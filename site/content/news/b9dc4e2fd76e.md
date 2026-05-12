+++
title = "广泛使用的 Daemon Tools 磁盘应用程序在长达一个月的供应链攻击中存在后门"
description = "Daemon Tools 用户：是时候检查您的计算机是否有隐秘感染了，stat"
seo_title = "广泛使用的 Daemon Tools 磁盘应用程序在长达一个月的供应链攻击中存在后门｜AI资讯解读 - AI热榜"
seo_description = "Daemon Tools 用户：是时候检查您的计算机是否有隐秘感染了，stat"
seo_keywords = "广泛使用的 Daemon Tools 磁盘应用程序在长达一个月的供应链攻击中存在后门, Ars Technica AI, AI新闻, AI资讯, AI热榜"
slug = "b9dc4e2fd76e"
type = "news"

[params]
id = "b9dc4e2fd76e"
name = "广泛使用的 Daemon Tools 磁盘应用程序在长达一个月的供应链攻击中存在后门"
title_en = "Widely used Daemon Tools disk app backdoored in monthlong supply-chain attack"
original_url = "https://arstechnica.com/security/2026/05/widely-used-daemon-tools-disk-app-backdoored-in-monthlong-supply-chain-attack/"
source = "Ars Technica AI"
published = "2026-05-05T19:46:15"
lang = "en"
intro = "Daemon Tools 用户：是时候检查您的计算机是否有隐秘感染了，stat"
ai_summary = "Daemon Tools 用户：是时候检查您的计算机是否有隐秘感染了，stat"
summary = "Daemon Tools users: It's time to check your machines for stealthy infections, stat."
summary_zh = "Daemon Tools 用户：是时候检查您的计算机是否有隐秘感染了，stat"
tags = []
list_page = 24
+++

<!-- AUTO-GENERATED: news page -->

Daemon Tools, a widely used app for mounting disk images, has been backdoored in a monthlong compromise that has pushed malicious updates from the servers of its developer, researchers said Tuesday.
Kaspersky, the security firm reporting the supply-chain attack, said it began on April 8 and remained active as of the time its post went live.

Installers that are signed by the developer’s official digital certificate and downloaded from its website infect Daemon Tools executables, causing the malware to run at boot time.

Kaspersky didn’t explicitly say so, but based on technical details, the infected versions appear to be only those that run on Windows.

Versions 12.5.0.2421 through 12.5.0.2434 are affected.

Neither Kaspersky nor developer AVB could be contacted immediately for additional details.
Hard to defend against
Infected versions contain an initial payload that collects MAC addresses, hostnames, DNS domain names, running processes, installed software, and system locales.

The malware sends them to an attacker-controlled server.

Thousands of machines in more than 100 countries were targeted.

Out of the many machines infected, about 12 of them, belonging to retail, scientific, government, and manufacturing organizations, have received a follow-on payload—an indication that the supply-chain attack targets select groups.
The incident is only the latest supply-chain attack.

Other such attacks include the poisoning of the CCleaner Windows utility in 2017, the Solar Winds app management software for enterprises in 2020, and 3CX VoIP client in 2023.

Such attacks are hard to defend against because users are infected when they do nothing more than install digitally signed updates available through official channels.

In all three cases it took weeks or months before the compromised update distribution channels were discovered.
“Based on our long-term experience of analyzing supply chain attacks, we can conclude that attackers orchestrated the DAEMON Tools compromise in a highly sophisticated manner,” Kaspersky researchers wrote.

“For example, the time it took to detect this attack, which turned out to be about one month, is comparable to the 3CX supply chain attack which we researched together with the cybersecurity community in 2023.

Given the high complexity of the attack, it is paramount for organizations to carefully examine machines that had DAEMON Tools installed, for abnormal cybersecurity-related activities that occurred on or after April 8.”

## 🔗 原始来源

如果你要核对细节，可以再看原文：
[Ars Technica AI原文链接](https://arstechnica.com/security/2026/05/widely-used-daemon-tools-disk-app-backdoored-in-monthlong-supply-chain-attack/)

