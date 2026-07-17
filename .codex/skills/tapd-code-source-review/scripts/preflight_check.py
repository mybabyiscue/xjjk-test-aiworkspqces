"""Create a code source review run and validate HTTP code URLs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Create tapd-code-source-review preflight outputs.")
    parser.add_argument("--code-url", action="append", required=True, help="HTTP/HTTPS code URL. Repeat for multiple services.")
    parser.add_argument("--output-root", default="output/code_sources", help="Output root for code source runs.")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    runs_dir = output_root / "runs"
    latest_dir = output_root / "latest"
    runs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    run_id = ensure_unique_run_id(runs_dir, now.strftime("%Y%m%d_%H%M%S_code_source"))
    run_dir = runs_dir / run_id
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)

    previous_run_id = read_previous_run_id(latest_dir)
    sources = []
    errors = []
    for index, url in enumerate(args.code_url, start=1):
        normalized, branch = normalize_git_url(url)
        service_id = resolve_name(normalized) or f"service_{index:03d}"
        parsed = urlparse(normalized)
        source_type = detect_source_type(normalized)
        error = ""
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            error = "代码路径必须是有效的 HTTP/HTTPS URL。"
            errors.append(f"{service_id}: {error}")
        sources.append(
            {
                "service_id": service_id,
                "input_url": normalized,
                "source_type": source_type,
                "resolved_name": resolve_name(normalized),
                "branch": branch,
                "commit": "",
                "cache_path": "",
                "fetch_status": "pending" if not error else "failed",
                "url_hash": hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16],
                "error": error,
            }
        )

    manifest = {
        "source_run_id": run_id,
        "previous_source_run_id": previous_run_id,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "code_sources": sources,
        "errors": errors,
    }
    confirmation = {
        "approved": False,
        "reason": "代码源准备阶段已初始化，等待代码获取、初步审查和人工确认。",
        "source_run_id": run_id,
        "approved_at": "",
        "approver": "",
    }

    write_json(run_dir / "source_manifest.json", manifest)
    write_json(run_dir / "code_source_confirmation.json", confirmation)
    write_input_check(run_dir / "input_check.md", manifest)
    sync_latest(run_dir, latest_dir)
    print(str(run_dir))
    return 1 if errors else 0


def detect_source_type(url: str) -> str:
    lower = url.lower().split("?", 1)[0]
    if lower.endswith(".git"):
        return "git"
    if lower.endswith(".zip"):
        return "zip"
    return "unknown"


def normalize_git_url(raw_url: str) -> tuple[str, str]:
    url = raw_url.strip()
    parsed = urlparse(url)
    marker = "/-/tree/"
    if marker not in parsed.path:
        return url, ""
    repository_path, branch = parsed.path.split(marker, 1)
    repository_url = parsed._replace(path=f"{repository_path}.git", params="", query="", fragment="").geturl()
    return repository_url, branch.strip("/")


def resolve_name(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    name = Path(path).name or "unknown-source"
    if name.endswith(".git"):
        name = name[:-4]
    if name.endswith(".zip"):
        name = name[:-4]
    return name or "unknown-source"


def ensure_unique_run_id(runs_dir: Path, base_run_id: str) -> str:
    candidate = base_run_id
    index = 1
    while (runs_dir / candidate).exists():
        candidate = f"{base_run_id}_{index:02d}"
        index += 1
    return candidate


def read_previous_run_id(latest_dir: Path) -> str:
    manifest_path = latest_dir / "source_manifest.json"
    if not manifest_path.exists():
        return ""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    return str(data.get("source_run_id", "")).strip()


def write_input_check(path: Path, manifest: dict) -> None:
    lines = [
        "# 代码源输入检查",
        "",
        f"- 运行ID：{manifest['source_run_id']}",
        f"- 上一次运行ID：{manifest.get('previous_source_run_id') or '无'}",
        f"- 检查结果：{'失败' if manifest.get('errors') else '通过'}",
        "",
        "## 代码来源",
        "",
        "| 服务编号 | 类型 | 名称 | URL | 状态 | 问题 |",
        "|---|---|---|---|---|---|",
    ]
    for item in manifest["code_sources"]:
        lines.append(
            f"| {item['service_id']} | {item['source_type']} | {item['resolved_name']} | {item['input_url']} | {item['fetch_status']} | {item.get('error') or '无'} |"
        )
    if manifest.get("errors"):
        lines.extend(["", "## 阻塞项", ""])
        lines.extend(f"- {error}" for error in manifest["errors"])
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def sync_latest(run_dir: Path, latest_dir: Path) -> None:
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(run_dir, latest_dir)


if __name__ == "__main__":
    raise SystemExit(main())
