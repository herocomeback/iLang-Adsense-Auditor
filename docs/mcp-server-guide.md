# MCP Server 封装与集成指南

本文档介绍如何将 **iLang AdSense Auditor** 封装为一个标准的 **MCP (Model Context Protocol) Server**，以便在支持 MCP 的主流 AI 编辑器（如 Cursor、Windsurf、Antigravity、VS Code 等）中实现无缝的本地项目诊断与代码修复闭环。

---

## 1. 概念厘清：Skill 与 MCP Server 的区别与协同

很多开发者会混淆 **Skill** 与 **MCP Server**，实际上两者处于 AI 体系的不同层级，相互补充：

| 维度 | **Skill (Agent 技能包 / Prompt 指南)** | **MCP Server (Model Context Protocol 服务)** |
| :--- | :--- | :--- |
| **本质** | **“如何思考与行动”的 SOP (Standard Operating Procedure)** | **“提供什么工具与数据”的 API 规范 (Tool / Resource)** |
| **存在形式** | Markdown 规则文件 (`SKILL.md`)，告诉 Agent 评估步骤、修复排期算法、报告撰写风格 | 可执行的服务程序（如 Python/Node.js），暴露标准化的 RPC/JSON-RPC 工具函数 |
| **驱动机制** | 由 LLM 自行阅读并遵守文本指引 | 由 IDE/Agent 宿主系统在合适的时候发起硬性函数调用（Tool Call） |
| **确定性** | 属于软性约束，依赖 LLM 的理解与遵循能力 | **强确定性**，代码逻辑死死卡住输入输出、文件读取与校验器运行 |
| **协作关系** | **大脑思维模式**：指示 AI“先调用 MCP 查 29 项，再按性价比排期，最后问站长要不要改代码”。 | **手脚与测量仪**：提供 `audit_project` 工具，自动抓取本地代码、运行 `audit_validator.py` 并返回硬核向量。 |

👉 **最强架构组合**：**MCP Server 负责“提供确定性的诊断工具”，Skill 负责“指导 AI 如何理解诊断结果并协助用户改代码”。**

---

## 2. MCP Server 架构设计

我们将把诊断引擎封装为一个 MCP Server，向 AI 编辑器暴露以下核心工具（Tool）：

- **`audit_project`**：输入本地项目路径 `project_path`（及可选线上 URL `site_url`），自动收集证据、运行完整的 29 项检测与 `audit_validator.py` 完整性校验，返回结构化的诊断结果 JSON。
- **`validate_audit_report`**：传入一个 JSON 报告路径，独立校验其完整性与屏障自洽性。

```mermaid
flowchart LR
    IDE["AI 编辑器 (Cursor / Windsurf / Antigravity)"] -- MCP JSON-RPC -- > MCP["mcp_server.py (MCP Server)"]
    MCP -- 1. 收集本地文件证据 -- > Workspace["本地工程源码 (Current Branch)"]
    MCP -- 2. 执行完整性校验 -- > Validator["validator/audit_validator.py"]
    Validator -- 3. 返回 29 项硬核向量与结论 -- > MCP
    MCP -- 4. 结构化结果 -- > IDE
```

---

## 3. Python MCP Server 完整实现代码

在项目根目录下创建 `mcp_server.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iLang AdSense Auditor — MCP Server Implementation
Exposes project auditing tools to MCP-compatible AI Editors.
"""

import json
import os
import sys
from mcp.server.fastmcp import FastMCP

# 引入项目自带的 validator
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "validator"))
import audit_validator

mcp = FastMCP("iLang AdSense Auditor")

@mcp.tool()
def list_requirements() -> str:
    """列出 AdSense 审核需覆盖的全部 29 条规则 ID 及其描述来源。"""
    ids = audit_validator.parse_registry()
    return json.dumps({"total": len(ids), "requirement_ids": ids}, ensure_ascii=False, indent=2)

@mcp.tool()
def audit_project(project_path: str, site_url: str = "") -> str:
    """
    诊断指定的本地项目代码与站点是否符合 Google AdSense 要求。
    
    :param project_path: 本地代码仓库绝对路径
    :param site_url: (可选) 部署的线上站点 URL
    :return: 包含 29 项完整评估模版与本地证据预查结果的 JSON 报告
    """
    if not os.path.exists(project_path):
        return f"Error: 路径不存在 '{project_path}'"

    # 1. 自动生成标准 29 项骨架
    template_str = audit_validator.make_template()
    report = json.loads(template_str)
    report["target"] = project_path if not site_url else f"{project_path} ({site_url})"

    # 2. 本地静态文件证据预查
    evidence_found = {}
    
    # 检查 robots.txt
    robots_path = os.path.join(project_path, "public", "robots.txt")
    if not os.path.exists(robots_path):
        robots_path = os.path.join(project_path, "robots.txt")
    if os.path.exists(robots_path):
        with open(robots_path, 'r', encoding='utf-8', errors='ignore') as f:
            evidence_found["robots.txt"] = f.read()[:500]
    else:
        evidence_found["robots.txt"] = "MISSING: 本地未找到 robots.txt 文件"

    # 检查必备页面文件
    pages = ["privacy", "about", "contact", "terms"]
    found_pages = []
    for root, _, files in os.walk(project_path):
        for file in files:
            file_lower = file.lower()
            for p in pages:
                if p in file_lower:
                    found_pages.append(os.path.relpath(os.path.join(root, file), project_path))
    evidence_found["detected_legal_pages"] = list(set(found_pages))

    result = {
        "status": "ready_for_llm_evaluation",
        "instructions": "请使用 SKILL.md 中的 AUDIT_JUDGE_v1 逻辑，结合上方 detected_evidence 对 29 条要求进行判定。",
        "detected_evidence": evidence_found,
        "skeleton_report": report
    }

    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
def validate_report(report_json_path: str) -> str:
    """
    校验指定 JSON 审核报告是否通过完整性闸门（是否覆盖全部 29 条规则且向量自洽）。
    
    :param report_json_path: 报告 JSON 文件的绝对路径
    """
    ok, msgs = audit_validator.check_report(report_json_path)
    return json.dumps({"passed": ok, "details": msgs}, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run()
```

---

## 4. 在 AI 编辑器中配置 MCP

依赖环境安装：
```bash
pip install mcp
```

### 在 Cursor / Windsurf / Antigravity / VS Code 中添加配置：

在你的编辑器 MCP 配置文件（如 `~/.cursor/mcp.json` 或 AI 编辑器的 MCP 设置界面）中加入，可以使用快捷启动脚本 `run_mcp.sh`（推荐，支持依赖自动检测与安装）：

```json
{
  "mcpServers": {
    "adsense-auditor": {
      "command": "/Users/your_username/Projects/iLang-Adsense-Auditor/run_mcp.sh"
    }
  }
}
```

---

## 5. 本地无缝工作流示范

配置完成后，你在 IDE 里切换任何项目或分支，均可使用如下流式交互：

1. **发起诊断**：
   在 IDE 聊天框输入：
   > `@adsense-auditor 请帮我诊断当前工程的 feature/adsense-prep 分支，线上域名是 https://example.com`

2. **自动触发 MCP**：
   IDE 自动调用 MCP 的 `audit_project` 工具，提取当前分支代码的 `robots.txt`、页面路由等证据。

3. **产出性价比排期**：
   AI 综合 MCP 返回的数据与技能指引，在侧边栏输出**人话结论与性价比修复表**（如：`OWN-02` 缺少 robots.txt 致命且成本低，排第 1；`DIS-01` 缺少隐私政策排第 2）。

4. **原址代码修改**：
   直接对 AI 说：
   > `按照排期第一项和第二项，直接帮我在当前工程创建 public/robots.txt 并补全隐私政策页面`

5. **代码预览与 Commit**：
   AI 直接改动本地代码，你可以随时通过 `git diff` 查看改动，确认无误后直接 Commit！
