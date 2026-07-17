# 在 Claude Code 里用

Claude Code 是 Anthropic 的命令行编程 agent。如果你会用终端、网站源码在本地,这是能让 AI **直接改你网站**的路径。

## 你需要先准备

- 装好 Claude Code
- 你要审核的网站地址(如果源码在本地,把仓库路径也备好)

## 装法

Claude Code 用的是 Agent Skills 开放标准,技能就是放在 skills 目录下的一个文件夹。

**个人技能**(所有项目可用),放到 `~/.claude/skills/`:

```bash
git clone https://github.com/adsorgcn/iLang-Adsense-Auditor.git
cp -r iLang-Adsense-Auditor/skill ~/.claude/skills/ilang-adsense-auditor
```

**项目级技能**(只在某个项目里用,可随 git 分享给团队),放到项目根目录的 `.claude/skills/` 下。

装完开一个新会话,Claude Code 会在启动时加载技能,并根据你的请求自动匹配。

## 开始审核

在你网站项目的目录里启动 Claude Code,然后说:

```
帮我审核这个网站能不能申请 Google AdSense,源码就在当前目录,别只看渲染后的首页,检查模板和内容来源
```

或者只给线上地址:

```
帮我审核 https://我的网站.com 能不能申请 Google AdSense
```

因为 Claude Code 能直接读你的代码,很多在纯网页版里「暂时无法判断」的项(内容是怎么生成的、路由怎么配的、robots.txt 里写了什么),它都能查实,报告更准。

## 让它直接帮你改(Claude Code 的强项)

审完之后,Claude Code 会主动问你「**需要我直接帮你改好吗**」。你说「改」,它就按「先改最划算的」顺序动手:改哪个文件、加什么内容,每一步对应一条要求,清清楚楚。改完可以让它重跑一遍审核,你会看到判定从阻断项变成通过。

涉及删内容、改主题、动 robots.txt 这类有风险的操作,它会先讲清后果、征得你同意。

## 顺带一提

Claude Code 也读项目根目录的 `AGENTS.md`(如果有)作为额外上下文。这个审核技能和你项目里已有的其他技能、配置可以共存,互不干扰。
