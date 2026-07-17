"""Scan fetched code sources for initial review findings."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


EXCLUDED_DIRS = {".git", "node_modules", "target", "build", "dist", ".idea", ".vscode", "__pycache__"}
TEXT_EXTENSIONS = {
    ".java", ".kt", ".xml", ".properties", ".yml", ".yaml", ".json", ".js", ".ts", ".py", ".go", ".php", ".sql", ".md"
}
RULES = [
    ("P1", "疑似敏感信息硬编码", re.compile(r"(?i)(password|passwd|pwd|token|secret|access[_-]?key)\s*[:=]\s*['\"][^'\"]{6,}")),
    ("P2", "存在 TODO/FIXME/临时代码", re.compile(r"(?i)\b(todo|fixme|临时|temporary|debug)\b")),
    ("P1", "疑似拼接 SQL", re.compile(r"(?i)(select|update|delete|insert)\s+.+\+.+")),
    ("P2", "疑似敏感日志输出", re.compile(r"(?i)(log\.|logger\.|console\.log).*(password|token|secret|authorization)")),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan code sources for initial prepare findings.")
    parser.add_argument("--manifest", required=True, help="Path to source_manifest.json.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_dir = manifest_path.parent
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    findings = []
    for source in manifest.get("code_sources", []):
        if source.get("fetch_status") != "success":
            continue
        cache_path = Path(source.get("cache_path", ""))
        if not cache_path.exists():
            findings.append(build_finding("P1", source, "", 0, "代码缓存路径不存在", "无法读取代码进行初步审查。"))
            continue
        findings.extend(scan_source(source, cache_path))

    (raw_dir / "prepare_findings.json").write_text(
        json.dumps({"findings": findings}, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    write_findings_markdown(run_dir / "code_prepare_findings.md", findings)
    sync_latest_if_run_dir(manifest_path)
    return 0


def scan_source(source: dict, root: Path) -> list[dict]:
    findings = []
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for priority, title, pattern in RULES:
                if pattern.search(line):
                    findings.append(
                        build_finding(priority, source, str(path), line_no, title, summarize_line(line))
                    )
    return findings


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if path.stat().st_size > 1024 * 1024:
            continue
        yield path


def build_finding(priority: str, source: dict, file_path: str, line: int, title: str, evidence: str) -> dict:
    return {
        "priority": priority,
        "service_id": source.get("service_id", ""),
        "service_name": source.get("resolved_name", ""),
        "file": file_path,
        "line": line,
        "title": title,
        "risk": "该问题可能影响后续代码证据分析或测试验证，需要人工确认。",
        "suggestion": "请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。",
        "evidence": evidence,
    }


def summarize_line(line: str) -> str:
    cleaned = line.strip()
    cleaned = re.sub(r"(?i)(password|passwd|pwd|token|secret|access[_-]?key)(\s*[:=]\s*)['\"][^'\"]+['\"]", r"\1\2\"***\"", cleaned)
    return cleaned[:240]


def write_findings_markdown(path: Path, findings: list[dict]) -> None:
    lines = ["# 代码源初步审查结果", ""]
    if not findings:
        lines.extend(["## 结论", "", "- 未发现明显阻塞项。", ""])
    else:
        lines.extend(["## 问题清单", ""])
        for index, item in enumerate(findings, start=1):
            lines.extend(
                [
                    f"### {index}. [{item['priority']}] {item['title']}",
                    "",
                    f"- 服务：{item['service_id']} / {item['service_name']}",
                    f"- 文件：{item['file'] or '无'}",
                    f"- 行号：{item['line'] or '无'}",
                    f"- 风险影响：{item['risk']}",
                    f"- 建议处理：{item['suggestion']}",
                    f"- 证据摘要：`{item['evidence']}`",
                    "",
                ]
            )
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def sync_latest_if_run_dir(manifest_path: Path) -> None:
    run_dir = manifest_path.parent
    if run_dir.name == "latest":
        return
    output_root = run_dir.parent.parent
    latest_dir = output_root / "latest"
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(run_dir, latest_dir)


if __name__ == "__main__":
    raise SystemExit(main())
