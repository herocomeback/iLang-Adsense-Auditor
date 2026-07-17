# 在 Codex 里用

Codex 是 OpenAI 的命令行编程 agent。它从 2025 年底开始支持 SKILL.md 技能标准,和 Claude Code 用的是同一套格式——所以这个审核器在 Codex 上零改造直接能用。

## 你需要先准备

- 装好 Codex CLI
- 你要审核的网站地址(源码在本地的话,把仓库路径也备好)

## 装法

Codex 从 skills 目录加载技能。

**个人技能**(所有项目可用),放到 `~/.codex/skills/`:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/adsorgcn/iLang-Adsense-Auditor.git
cp -r iLang-Adsense-Auditor/skill ~/.codex/skills/ilang-adsense-auditor
```

**项目级技能**(随 git 分享给团队),放到项目根目录的 `.codex/skills/` 下。

装完开一个新的 Codex 会话即可。

## 开始审核

Codex 有两种触发方式:

**自动触发**——直接说需求,Codex 会根据技能描述自动匹配:

```
帮我审核这个网站能不能申请 Google AdSense,源码在当前目录
```

**显式调用**——用 `$` 加技能名点名调用:

```
$ilang-adsense-auditor 审核 https://我的网站.com
```

Codex 能执行代码,所以完整性自检这道程序把关是硬性的——29 条要求一条都漏不掉。

## 让它直接帮你改

审完之后 Codex 会主动问你要不要直接改。同意后它按性价比顺序动手,每处修复对应一条要求。涉及有风险的改动会先征得你同意。

## 跨工具通用

这个技能用的是 Agent Skills 开放标准。同一份技能文件在 Codex、Claude Code、OpenClaw、Cursor、Gemini CLI 之间通用——你在一个工具里装好,复制到另一个工具的 skills 目录就能用,不需要任何改动。
