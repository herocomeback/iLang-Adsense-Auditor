# 在 Hermes 里用

Hermes 是 Nous Research 出的开源 agent,特点是技能以 SKILL.md 文档形式存储,遇到匹配场景自动加载。

## 你需要先准备

- 一个能跑的 Hermes 环境
- 你要审核的网站地址

## 装法一:从官方 Skills Hub 装(如果已收录)

```bash
hermes skills browse            # 浏览可用技能
hermes skills install ilang-adsense-auditor
hermes skills inspect ilang-adsense-auditor   # 装完看详情
```

## 装法二:从 GitHub 手动放

Hermes 的技能就是一个目录,里面一个 SKILL.md(可选 references/)。把本仓库的 `skill/` 目录放进 Hermes 的 skills 目录即可:

```bash
git clone https://github.com/adsorgcn/iLang-Adsense-Auditor.git
cp -r iLang-Adsense-Auditor/skill <你的 Hermes skills 目录>/ilang-adsense-auditor
```

本仓库的目录结构(`SKILL.md` + `references/` + `validator/`)正好符合 Hermes 的技能格式,不需要改动。

## 开始审核

跟你的 agent 说:

```
帮我审核 https://我的网站.com 能不能申请 Google AdSense
```

Hermes 会根据 SKILL.md 里的描述自动匹配场景、加载技能。它能执行 Python,所以完整性自检这道程序把关是硬性的。

## 让它直接帮你改

如果网站源码在 Hermes 能访问的位置,审完它会主动问你要不要直接改。同意后按性价比顺序动手。

## 一个 Hermes 特有的好处

Hermes 会从经验里学习。你用这个审核器审过几次之后,它可能会把审核过程中形成的可复用工作流沉淀下来,下次审得更顺。这是 Hermes 的机制,不需要你额外做什么。
