#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iLang AdSense Auditor — MCP Server
===================================
把 iLang AdSense 审核引擎与 29 项完整性闸门封装为标准的 MCP (Model Context Protocol) 服务。
支持在 Cursor、Windsurf、Antigravity、VS Code 等 IDE 中通过 MCP 协议进行项目诊断与代码修复。

依赖安装:
  pip install mcp

启动方式:
  python3 mcp_server.py
"""

import json
import os
import sys

# 引入项目自带的 validator 模块
HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR_DIR = os.path.join(HERE, "validator")
if VALIDATOR_DIR not in sys.path:
    sys.path.insert(0, VALIDATOR_DIR)

import audit_validator

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("❌ 错误: 未检测到 Python `mcp` 依赖库。", file=sys.stderr)
    print("👉 请先在终端运行以下命令进行安装:", file=sys.stderr)
    print("   pip install mcp\n", file=sys.stderr)
    sys.exit(1)

# 初始化 MCP 服务
mcp = FastMCP("iLang AdSense Auditor")


@mcp.tool()
def get_skill_instructions() -> str:
    """
    获取 iLang AdSense Auditor 的完整 Skill 评估规范与 SOP 指导。
    包含 29 项检测逻辑、AUDIT_JUDGE_v1 判定向量定义、屏障聚合规则与代修指引。
    """
    skill_path = os.path.join(HERE, "skill", "SKILL.md")
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Error: SKILL.md 文件未找到。"


@mcp.tool()
def list_requirements() -> str:
    """
    列出 Google AdSense 审核必须覆盖的全部 29 条规则 ID 及其要求列表。
    数据源来自 skill/references/requirements.md
    """
    try:
        ids = audit_validator.parse_registry()
        return json.dumps({
            "total_count": len(ids),
            "requirement_ids": ids,
            "source_file": "skill/references/requirements.md"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def audit_project(project_path: str, site_url: str = "") -> str:
    """
    扫描指定的本地代码工程，预查静态证据（如 robots.txt、sitemap、合规页面），
    并生成涵盖全部 29 条 ID 的标准判断模版报告。

    :param project_path: 本地代码工程的绝对路径 (如 /Users/xxx/Projects/my-website)
    :param site_url: (可选) 已部署的线上 URL (如 https://my-website.com)
    """
    if not os.path.exists(project_path):
        return json.dumps({"error": f"项目路径不存在: {project_path}"}, ensure_ascii=False)

    # 1. 生成标准的 29 项报告模版
    template_str = audit_validator.make_template()
    report = json.loads(template_str)
    report["target"] = project_path if not site_url else f"{project_path} ({site_url})"
    report["audit_type"] = "pre-application"

    # 2. 自动抓取本地静态证据
    evidence = {}

    # 检查 robots.txt
    possible_robots = [
        os.path.join(project_path, "public", "robots.txt"),
        os.path.join(project_path, "static", "robots.txt"),
        os.path.join(project_path, "robots.txt"),
    ]
    found_robots = None
    for path in possible_robots:
        if os.path.exists(path):
            found_robots = path
            break

    if found_robots:
        try:
            with open(found_robots, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(1000)
                evidence["robots_txt"] = {
                    "path": os.path.relpath(found_robots, project_path),
                    "content_snippet": content,
                    "has_mediapartners_google": "mediapartners-google" in content.lower()
                }
        except Exception as e:
            evidence["robots_txt"] = {"error": str(e)}
    else:
        evidence["robots_txt"] = {"status": "MISSING", "warning": "未找到 robots.txt 文件"}

    # 扫描必备页面与法务披露文件 (privacy, about, contact, terms)
    legal_keywords = ["privacy", "about", "contact", "terms", "disclaimer", "sitemap"]
    found_legal_files = []
    
    # 忽略常见不需要扫描的大型文件夹
    ignore_dirs = {".git", "node_modules", ".next", "dist", "build", "vendor"}

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            file_lower = file.lower()
            if any(kw in file_lower for kw in legal_keywords):
                rel_path = os.path.relpath(os.path.join(root, file), project_path)
                found_legal_files.append(rel_path)

    evidence["detected_files"] = found_legal_files

    result = {
        "status": "ready_for_llm_evaluation",
        "instructions": (
            "请遵循 SKILL.md 规则，结合下方 detected_evidence 对 29 条 requirement_ids 进行判定。"
            "每个 ID 填入五维向量 AUDIT_JUDGE_v1 (cmp, evd, cer, imp, fix)，"
            "并按照屏障规则推导 site_verdict，然后生成按性价比排序的人话诊断报告。"
        ),
        "detected_evidence": evidence,
        "skeleton_report": report
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def validate_report(report_json_path: str) -> str:
    """
    运行完整性硬闸门校验，验证审核报告 JSON 是否覆盖全部 29 条要求且向量自洽。

    :param report_json_path: 报告 JSON 文件的绝对路径
    """
    if not os.path.exists(report_json_path):
        return json.dumps({"passed": False, "errors": [f"文件不存在: {report_json_path}"]})

    ok, msgs = audit_validator.check_report(report_json_path)
    return json.dumps({
        "passed": ok,
        "messages": msgs
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
