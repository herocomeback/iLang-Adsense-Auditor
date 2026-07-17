# 在 OpenClaw 里用

OpenClaw 是开源的个人 AI agent。如果你已经跑起来了 OpenClaw,装这个审核器只需要一条命令。

## 你需要先准备

- 一个能跑的 OpenClaw 环境
- 你要审核的网站地址

## 装法一:从 ClawHub 装(如果已发布)

```bash
openclaw skills install ilang-adsense-auditor
```

装之前建议先看一眼技能内容(第三方技能都应视为不可信代码,先读再启用):

```bash
openclaw skills verify ilang-adsense-auditor
```

## 装法二:从 GitHub 直接装

把仓库克隆到你的 skills 目录:

```bash
git clone https://github.com/adsorgcn/iLang-Adsense-Auditor.git
cp -r iLang-Adsense-Auditor/skill ~/.openclaw/skills/ilang-adsense-auditor
```

> 说明:本仓库的 SKILL.md 在 `skill/` 目录下。上面这条命令把整个 `skill/` 目录复制过去并改名为技能名。如果你用 `--global` 装到共享目录,所有本地 agent 都能用。

装完后 OpenClaw 会在下一次会话自动加载这个技能。

## 开始审核

跟你的 agent 说:

```
帮我审核 https://我的网站.com 能不能申请 Google AdSense
```

OpenClaw 会根据技能的 description 自动匹配并触发。它会抓取网站、逐条检查、跑完整性自检(OpenClaw 能执行 Python,所以这道程序把关是硬性的),然后给报告。

## 让它直接帮你改

如果你的网站源码在 OpenClaw 能访问的地方,审完它会主动问你「需要我直接帮你改好吗」。同意后它按「先改最划算的」顺序动手。涉及有风险的改动(删内容、动 robots.txt)会先征得你同意。

## 安全提醒

OpenClaw 官方一贯建议:把第三方技能当作不可信代码,启用前先读一遍,风险操作用沙盒运行。这个技能是纯审核 + 修复工具,核心是一个零依赖的 Python 校验器和一份要求清单,你可以完整审阅后再启用。
