#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iLang AdSense Auditor — audit validator
=======================================

The completeness gate. Turns "please check every item" from a polite request
the model may ignore into a mechanical guarantee: an audit report that misses a
requirement ID, malforms a judgment vector, or states a site verdict that does
not follow from its own findings exits non-zero.

Reads the requirement registry (skill/references/requirements.md) as the single
source of truth for which IDs must be covered, so when Google's policies change
and rows are edited, the gate updates from that one file with no code change.

Stdlib only. No dependencies.

Subcommands
-----------
  --template            emit a blank report skeleton covering every requirement ID
  --check REPORT.json   enforce completeness + schema + barrier consistency
  --list                print every requirement ID parsed from the registry
  --selftest            run built-in self checks

Usage
-----
  python3 audit_validator.py --template > report.json
  python3 audit_validator.py --check report.json
  python3 audit_validator.py --list
  python3 audit_validator.py --selftest
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.normpath(os.path.join(HERE, "..", "skill", "references", "requirements.md"))

DIMS = ["cmp", "evd", "cer", "imp", "fix"]
VERDICTS = {"PASS", "BLOCKER", "HIGH", "MEDIUM", "UNKNOWN", "NA"}
SITE_VERDICTS = {"READY", "READY_AFTER_FIXES", "NOT_READY"}

# Match a requirement id at the start of a markdown table cell: | OWN-01 | ...
ID_RE = re.compile(r"^\|\s*([A-Z]{3}-\d{2})\s*\|")


def parse_registry(path=REGISTRY):
    """Extract the ordered, de-duplicated list of requirement IDs from the registry."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"requirement registry not found: {path}")
    ids = []
    seen = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = ID_RE.match(line)
            if m:
                rid = m.group(1)
                if rid not in seen:
                    seen.add(rid)
                    ids.append(rid)
    if not ids:
        raise ValueError("no requirement IDs parsed from registry; format may have changed")
    return ids


def derive_site_verdict(verdicts):
    """Barrier aggregation: one BLOCKER vetoes; else HIGH/MEDIUM/UNKNOWN need fixes; else READY."""
    vs = set(verdicts)
    if "BLOCKER" in vs:
        return "NOT_READY"
    if "HIGH" in vs:
        return "READY_AFTER_FIXES"
    if "MEDIUM" in vs or "UNKNOWN" in vs:
        return "READY_AFTER_FIXES"
    return "READY"


def _err(errors, msg):
    errors.append(msg)


def validate_record(rec, errors):
    """Validate a single per-requirement record. Appends messages to errors."""
    rid = rec.get("id", "<no-id>")

    verdict = rec.get("verdict")
    if verdict not in VERDICTS:
        _err(errors, f"{rid}: verdict '{verdict}' not one of {sorted(VERDICTS)}")

    v = rec.get("v")
    if not isinstance(v, dict):
        _err(errors, f"{rid}: missing or non-object vector 'v'")
        v = {}
    for k in DIMS:
        if k not in v:
            _err(errors, f"{rid}: vector missing dimension '{k}'")
            continue
        val = v[k]
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            _err(errors, f"{rid}: dimension '{k}' is not a number: {val!r}")
        elif not (0.0 <= float(val) <= 1.0):
            _err(errors, f"{rid}: dimension '{k}'={val} outside [0.00, 1.00]")
    extra = set(v) - set(DIMS)
    if extra:
        _err(errors, f"{rid}: vector has unknown dimensions {sorted(extra)}")

    # string fields
    for field in ("issue", "evidence", "basis"):
        if not isinstance(rec.get(field), str) or not rec.get(field).strip():
            _err(errors, f"{rid}: field '{field}' must be a non-empty string")
    fixv = rec.get("fix")
    if not isinstance(fixv, str):
        _err(errors, f"{rid}: field 'fix' must be a string")
    elif not fixv.strip() and verdict not in ("PASS", "NA"):
        _err(errors, f"{rid}: field 'fix' may be empty only when verdict is PASS or NA")

    # vector/verdict coherence
    cmp = v.get("cmp")
    if isinstance(cmp, (int, float)) and not isinstance(cmp, bool):
        if verdict == "PASS" and float(cmp) < 0.5:
            _err(errors, f"{rid}: verdict PASS but compliance cmp={cmp} < 0.5")
        if verdict == "BLOCKER" and float(cmp) > 0.5:
            _err(errors, f"{rid}: verdict BLOCKER but compliance cmp={cmp} > 0.5")


def check_report(report_path):
    """Full report check. Returns (ok: bool, messages: list[str])."""
    messages = []
    required_ids = parse_registry()

    try:
        with open(report_path, encoding="utf-8") as f:
            report = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return False, [f"cannot read report: {e}"]

    findings = report.get("findings")
    if not isinstance(findings, list):
        return False, ["report has no 'findings' array"]

    errors = []

    # per-record validation
    seen_ids = []
    for rec in findings:
        if not isinstance(rec, dict):
            _err(errors, f"finding is not an object: {rec!r}")
            continue
        validate_record(rec, errors)
        rid = rec.get("id")
        if rid is not None:
            seen_ids.append(rid)

    # completeness gate
    seen_set = set(seen_ids)
    required_set = set(required_ids)

    missing = [r for r in required_ids if r not in seen_set]
    if missing:
        _err(errors, f"INCOMPLETE: {len(missing)} requirement ID(s) not covered: {missing}")

    unknown = [r for r in seen_ids if r not in required_set]
    if unknown:
        _err(errors, f"unknown requirement ID(s) not in registry: {sorted(set(unknown))}")

    dupes = sorted({r for r in seen_ids if seen_ids.count(r) > 1})
    if dupes:
        _err(errors, f"duplicate requirement ID(s): {dupes}")

    # barrier consistency: stated site verdict must equal derived
    verdicts = [rec.get("verdict") for rec in findings if isinstance(rec, dict)]
    valid_verdicts = [x for x in verdicts if x in VERDICTS]
    derived = derive_site_verdict(valid_verdicts)
    stated = report.get("site_verdict")
    if stated not in SITE_VERDICTS:
        _err(errors, f"site_verdict '{stated}' not one of {sorted(SITE_VERDICTS)}")
    elif stated != derived:
        _err(errors, f"site_verdict '{stated}' contradicts findings; barrier rule derives '{derived}'")

    if errors:
        return False, errors

    messages.append(f"OK: 全部 {len(required_ids)} 条要求均被覆盖且各一次")
    messages.append(f"OK: 站点结论 '{stated}' 与各条判定自洽")
    return True, messages


def make_template():
    """Emit a blank report skeleton covering every requirement ID."""
    ids = parse_registry()
    findings = []
    for rid in ids:
        findings.append({
            "id": rid,
            "verdict": "UNKNOWN",
            "v": {"cmp": 0.0, "evd": 0.0, "cer": 0.0, "imp": 0.5, "fix": 0.5},
            "issue": "TODO: describe the finding for this requirement",
            "evidence": "TODO: cite the concrete evidence observed",
            "basis": f"see requirements.md {rid}",
            "fix": "TODO: exact remediation, or empty if PASS/NA",
        })
    report = {
        "target": "TODO: URL or repo path",
        "audit_type": "pre-application",
        "site_verdict": "READY_AFTER_FIXES",
        "findings": findings,
    }
    return json.dumps(report, ensure_ascii=False, indent=2)


def selftest():
    """Built-in self checks covering the gate's core guarantees."""
    ids = parse_registry()
    assert len(ids) == len(set(ids)), "registry IDs not unique"
    print(f"[selftest] registry parses {len(ids)} unique IDs")

    # barrier logic
    assert derive_site_verdict(["PASS", "NA"]) == "READY"
    assert derive_site_verdict(["PASS", "MEDIUM"]) == "READY_AFTER_FIXES"
    assert derive_site_verdict(["PASS", "UNKNOWN"]) == "READY_AFTER_FIXES"
    assert derive_site_verdict(["PASS", "HIGH", "MEDIUM"]) == "READY_AFTER_FIXES"
    assert derive_site_verdict(["PASS", "BLOCKER", "HIGH"]) == "NOT_READY"
    print("[selftest] barrier aggregation correct (BLOCKER vetoes, averages never launder)")

    # a full valid report passes
    full = json.loads(make_template())
    # turn the template into an all-PASS report to test READY
    for rec in full["findings"]:
        rec["verdict"] = "PASS"
        rec["v"] = {"cmp": 0.9, "evd": 0.9, "cer": 0.9, "imp": 0.8, "fix": 0.9}
        rec["issue"] = "satisfied"
        rec["evidence"] = "observed"
        rec["basis"] = "reg"
        rec["fix"] = ""
    full["site_verdict"] = "READY"
    tmp = os.path.join(HERE, "_selftest_report.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(full, f)
    ok, msgs = check_report(tmp)
    assert ok, f"valid report rejected: {msgs}"
    print("[selftest] complete all-PASS report accepted")

    # dropping one finding must fail the completeness gate
    full["findings"].pop()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(full, f)
    ok, msgs = check_report(tmp)
    assert not ok and any("INCOMPLETE" in m for m in msgs), "gate did not catch missing ID"
    print("[selftest] missing ID correctly rejected (completeness gate works)")

    # a BLOCKER with stated READY must fail barrier consistency
    full = json.loads(make_template())
    for rec in full["findings"]:
        rec["verdict"] = "PASS"
        rec["v"] = {"cmp": 0.9, "evd": 0.9, "cer": 0.9, "imp": 0.8, "fix": 0.9}
        rec["issue"] = "x"; rec["evidence"] = "x"; rec["basis"] = "x"; rec["fix"] = ""
    full["findings"][0]["verdict"] = "BLOCKER"
    full["findings"][0]["v"]["cmp"] = 0.0
    full["findings"][0]["fix"] = "fix it"
    full["site_verdict"] = "READY"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(full, f)
    ok, msgs = check_report(tmp)
    assert not ok and any("contradicts" in m for m in msgs), "barrier consistency not enforced"
    print("[selftest] site verdict contradicting a BLOCKER correctly rejected")

    os.remove(tmp)
    print("[selftest] ALL PASSED")


def main():
    ap = argparse.ArgumentParser(description="iLang AdSense Auditor — completeness gate & schema validator")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--template", action="store_true", help="emit a blank report skeleton")
    g.add_argument("--check", metavar="REPORT", help="check a report for completeness + schema + barrier consistency")
    g.add_argument("--list", action="store_true", help="list requirement IDs from the registry")
    g.add_argument("--selftest", action="store_true", help="run built-in self checks")
    args = ap.parse_args()

    if args.template:
        print(make_template())
    elif args.list:
        for rid in parse_registry():
            print(rid)
    elif args.selftest:
        selftest()
    elif args.check:
        ok, msgs = check_report(args.check)
        for m in msgs:
            print(("  通过  " if ok else "  失败  ") + m)
        if not ok:
            print(f"\n发现 {len(msgs)} 处问题;审核在结构上不完整或不自洽。", file=sys.stderr)
            sys.exit(1)
        print("\n审核通过完整性闸门。")


if __name__ == "__main__":
    main()
