#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iLang AdSense Auditor — MCP Server (Enhanced Version)
=====================================================
把 iLang AdSense 审核引擎与 29 项完整性闸门（含 73 项细化检测点预查与模版生成）封装为标准的 MCP 服务。
支持在 Cursor、Windsurf、Antigravity、VS Code 等 IDE 中通过 MCP 协议进行项目诊断与代码修复。

依赖安装:
  pip install mcp

启动方式:
  python3 mcp_server.py
"""

import json
import os
import re
import sys

# 引入项目自带的 validator 模块
HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR_DIR = os.path.join(HERE, "validator")
if VALIDATOR_DIR not in sys.path:
    sys.path.insert(0, VALIDATOR_DIR)

import audit_validator

try:
    # mcp 2.x
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    try:
        # mcp 1.x
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        try:
            # standalone fastmcp
            from fastmcp import FastMCP
        except ImportError:
            print("❌ 错误: 未检测到 Python `mcp` 依赖库。", file=sys.stderr)
            print("👉 请先在终端运行以下命令进行安装:", file=sys.stderr)
            print("   pip install mcp\n", file=sys.stderr)
            sys.exit(1)

# 初始化 MCP 服务
mcp = FastMCP("iLang AdSense Auditor")


@mcp.tool()
def get_prompt_templates() -> str:
    """
    获取常用的 AdSense 诊断提示词模版列表（申请前全量诊断、被拒诊断、修复复审、跨项目诊断）。
    方便用户直接复制模版并替换 [路径] 或 [URL] 即可使用。
    """
    templates = {
        "title": "📋 iLang AdSense Auditor 常用提示词填空模版",
        "instructions": "请选择适合你当前场景的模版，复制后替换方括号 [] 中的内容发送即可：",
        "templates": [
            {
                "id": "template_pre_application",
                "name": "模版 1：申请前全量诊断 + 本地代码直接代修 (最常用)",
                "copy_text": "用 adsense-auditor 结合本地代码和线上站点帮我做全量合规诊断：\n- 本地路径：[你的本地工程路径, 如 /Users/xxx/Projects/my-app]\n- 线上 URL：[你的线上网址, 如 https://example.com]\n- 阶段：申请前预查\n要求：按性价比给出修复排期，并直接在本地工程中帮我修改代码！"
            },
            {
                "id": "template_post_rejection",
                "name": "模版 2：被拒后的拒审原因诊断与内容扩充 (低价值内容/网站未准备好)",
                "copy_text": "我的 AdSense 申请被拒了，请用 adsense-auditor 帮我诊断原因并给出扩充方案：\n- 本地路径：[你的本地工程路径]\n- 线上 URL：[你的线上网址]\n- 拒信原文：[在此粘贴 AdSense 后台拒信原文]\n要求：映射拒信原因到对应规则，给出内容扩充策略并直接在本地帮我修改代码。"
            },
            {
                "id": "template_post_fix",
                "name": "模版 3：代码修复后的复审验证 (重新提交审核前)",
                "copy_text": "我已经按建议修改了代码，请用 adsense-auditor 帮我复审是否具备重新提交条件：\n- 本地路径：[你的本地工程路径]\n- 线上 URL：[你的线上网址]\n- 已修复内容：[如：增加了 Privacy 页面和游戏底部的富文本指南]\n要求：重新跑一遍 29 项硬闸门校验，确认阻断项清零并提示最佳重新提交时间。"
            },
            {
                "id": "template_cross_project",
                "name": "模版 4：跨项目/跨目录诊断 (指定其他工程路径)",
                "copy_text": "请用 adsense-auditor 帮我诊断本地另一个项目：\n- 目标工程绝对路径：[另一个项目的绝对路径, 如 /Users/xxx/Projects/another-app]\n- 线上 URL：[网址(可选)]\n请抓取该路径静态证据，给出 29 项矢量诊断与性价比修复建议。"
            },
            {
                "id": "template_minimal",
                "name": "模版 5：极简一句话 Prompt (快捷触发)",
                "copy_text": "用 adsense-auditor 诊断项目 [你的本地路径]，按性价比给出修复排期，并直接帮我改好本地代码。"
            }
        ]
    }
    return json.dumps(templates, ensure_ascii=False, indent=2)


@mcp.tool()
def get_skill_instructions() -> str:
    """
    获取 iLang AdSense Auditor 的完整 Skill 评估规范与 SOP 指导。
    包含 29 项检测逻辑（融入 73 项细分规则）、AUDIT_JUDGE_v1 判定向量定义、屏障聚合规则与代修指引。
    """
    skill_path = os.path.join(HERE, "skill", "SKILL.md")
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Error: SKILL.md 文件未找到。"


@mcp.tool()
def list_requirements() -> str:
    """
    列出 Google AdSense 审核必须覆盖的全部 29 条规则 ID 及其要求列表与 73 项子检测点映射。
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
    扫描指定的本地代码工程，预查静态证据（含 robots.txt、ads.txt、欺骗性下载按钮/假播放键、
    PII/敏感表单、COPPA/CMP、POST 渲染墙等细化特征），并生成标准的 29 项评估模版。

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

    # 2. 自动抓取本地静态证据与细化特征扫描
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

    # 检查 ads.txt
    possible_ads_txt = [
        os.path.join(project_path, "public", "ads.txt"),
        os.path.join(project_path, "ads.txt"),
    ]
    found_ads_txt = None
    for path in possible_ads_txt:
        if os.path.exists(path):
            found_ads_txt = path
            break
    if found_ads_txt:
        try:
            with open(found_ads_txt, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(500)
                evidence["ads_txt"] = {
                    "path": os.path.relpath(found_ads_txt, project_path),
                    "content": content,
                    "has_google_pub": "google.com" in content.lower() and "pub-" in content.lower()
                }
        except Exception as e:
            evidence["ads_txt"] = {"error": str(e)}

    # 扫描必备页面与法务披露文件
    legal_keywords = ["privacy", "about", "contact", "terms", "disclaimer", "sitemap", "methodology"]
    found_legal_files = []
    ignore_dirs = {".git", "node_modules", ".next", "dist", "build", "vendor"}

    # 细分风险特征触发器记录
    deceptive_button_signals = []
    pii_sensitive_signals = []
    consent_cmp_signals = []

    deceptive_btn_re = re.compile(r'(fake-ad|download-btn|play-now-btn|deceptive-cta|start-download)', re.IGNORECASE)
    pii_re = re.compile(r'(social-security|ssn-input|passport-number|credit-card-number)', re.IGNORECASE)
    cmp_re = re.compile(r'(cookiebanner|consentmanager|gdpr-consent|coppa)', re.IGNORECASE)

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            file_lower = file.lower()
            rel_file = os.path.relpath(os.path.join(root, file), project_path)

            if any(kw in file_lower for kw in legal_keywords):
                found_legal_files.append(rel_file)

            if file_lower.endswith(('.html', '.jsx', '.tsx', '.astro', '.vue', '.js', '.ts')):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read(5000)
                        if deceptive_btn_re.search(file_content):
                            deceptive_button_signals.append(rel_file)
                        if pii_re.search(file_content):
                            pii_sensitive_signals.append(rel_file)
                        if cmp_re.search(file_content):
                            consent_cmp_signals.append(rel_file)
                except Exception:
                    pass

    evidence["detected_files"] = found_legal_files
    evidence["risk_signals_scan"] = {
        "deceptive_ctas_detected": deceptive_button_signals[:5],
        "pii_sensitive_inputs_detected": pii_sensitive_signals[:5],
        "consent_cmp_components_detected": consent_cmp_signals[:5]
    }

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
