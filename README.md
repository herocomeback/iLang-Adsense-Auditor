# iLang AdSense 审核器

**用真正的判断层做 AdSense 过审审核——每条判定都是可解释的判断向量,站点结论由屏障规则推导,完整性由代码强制,不靠模型自觉。**

这是 [I-Lang v5.0 判断层](https://github.com/ilang-ai/ilang-spec) 落到具体商业场景的第一个垂直示范:审核一个网站是否具备申请 Google AdSense 的条件。

一句话:这不是又一个 AdSense 检查清单,而是把「审核判断」升级为结构化判断协议的示范——每条判定输出可解释的判断向量,站点结论由屏障逻辑推导,完整性由校验器强制,全程留痕。

---

## 为什么要做这个

市面上每一个 AdSense 审核工具都有同样的两个结构性缺陷:

1. **判定只是一个词。**「不合格」这三个字,没告诉你这个判断有多确定、对过审的实际威胁有多大、修复起来有多贵——这些本是不同的维度,却被糊成了一个词。
2. **完整性靠嘴上说。** 工具告诉模型「请检查每一项」,然后寄希望于它照做。它到底查全了没有,无法验证。

本项目在协议层解决这两个问题:

- **判断向量,而非标签。** 每条要求输出一个 5 维判断记录——合规度、证据质量、确定性、过审影响、修复成本,全部在 `[0.00, 1.00]` 区间、统一极性,外加一个明确判定。每个判定背后的「为什么」都是可量化、可复算、可争议的数字。
- **屏障聚合,而非平均。** 站点级结论遵循 I-Lang v5.0 的屏障原则:任何一个 `BLOCKER`(阻断项)一票否决整个申请,无论其他项分数多高。平均值永远无法把一个硬性违规洗白。
- **完整性由代码强制。** `validator/audit_validator.py`(纯标准库)解析要求清单,检查审核报告是否**恰好覆盖每一个 ID 一次**,校验每个向量字段,并验证站点结论确实由各条判定推导而来。漏掉一条要求不是「疏忽」,是一个非零退出码。

## 这个项目不是什么

诚实是设计的一部分:

- **它不是过审预测器。** Google 的审核包含人工判断和未公开的标准。一次完美的审核能提高你的胜算、消除已知的阻断项,但**无法保证过审**,本项目也从不作此承诺。
- **实时官方文档永远优先。** 政策会变。skill 要求在正式审核前先刷新官方文档;本清单是对这些政策的结构化索引,而非替代品。

## Clean-room 声明

本项目完全基于 Google 官方公开政策文档(AdSense 帮助中心、Google 发布商政策)构建,不含任何来自第三方审核工具或清单的内容。要求清单、判断 schema、校验器均为原创作品。

## 仓库结构

```
skill/
  SKILL.md                     agent skill(Claude 格式,I-Lang 结构化协议)
  references/
    requirements.md            clean-room 要求清单(ID、官方依据、证据要点)
    judgment-schema.md         AUDIT_JUDGE_v1 判断记录 + 屏障聚合规则
    usage.md                   调用模板
validator/
  audit_validator.py           完整性闸门 + schema 一致性校验(纯标准库)
examples/
  sample-audit.json            一份通过 --check 的完整审核报告
```

## 快速开始

```bash
# 生成一份覆盖所有要求 ID 的空白报告骨架
python3 validator/audit_validator.py --template > report.json

# ……执行审核(agent 填充各条判断记录)……

# 强制校验完整性 + schema + 屏障一致性
python3 validator/audit_validator.py --check report.json
```

非零退出即代表审核在结构上不完整或不自洽。这正是设计目的。

## 与 I-Lang v5.0 的关系

这里的判断 schema 是 I-Lang v5.0 判断层的一个**领域剖面**(domain profile):同样的哲学(统一极性、屏障独立于加权分数、判定全程留痕),应用到一个有界的垂直领域。判断层本身的可学性,在 [ilang-Benchmark/judgment](https://github.com/ilang-ai/ilang-Benchmark) 里另有实证。

## 许可

MIT © 2026 iLang Inc.
