"""Fetch or update code sources from a source_manifest.json."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch code sources for tapd-code-source-review.")
    parser.add_argument("--manifest", required=True, help="Path to source_manifest.json.")
    parser.add_argument("--output-root", default="output/code_sources", help="Output root for cache directories.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_root = Path(args.output_root)
    cache_root = output_root / "cache"
    errors = []

    for source in manifest.get("code_sources", []):
        try:
            fetch_source(source, cache_root)
        except Exception as exc:  # noqa: BLE001 - preserve original failure for report
            source["fetch_status"] = "failed"
            source["error"] = str(exc)
            errors.append(f"{source.get('service_id')}: {exc}")

    manifest["errors"] = list(dict.fromkeys([*manifest.get("errors", []), *errors]))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    write_fetch_result(manifest_path.parent / "code_fetch_result.md", manifest)
    sync_latest_if_run_dir(manifest_path)
    return 1 if errors else 0


def fetch_source(source: dict, cache_root: Path) -> None:
    source_type = source.get("source_type")
    if source_type == "git":
        fetch_git(source, cache_root / source["resolved_name"])
        return
    if source_type == "zip":
        fetch_zip(source, cache_root / "archives" / source["url_hash"])
        return
    raise ValueError("暂不支持无法识别的代码来源类型，请提供 .git 或 .zip 地址。")


def fetch_git(source: dict, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    url = source["input_url"]
    if target.exists() and (target / ".git").exists():
        run_git(["git", "-C", str(target), "fetch", "--all", "--prune"])
    else:
        if target.exists():
            shutil.rmtree(target)
        run_git(["git", "clone", "--quiet", url, str(target)])
    requested_branch = str(source.get("branch", "")).strip()
    if requested_branch:
        run_git(["git", "-C", str(target), "checkout", "--quiet", "-B", requested_branch, f"origin/{requested_branch}"])
    commit = run_git(["git", "-C", str(target), "rev-parse", "HEAD"]).strip()
    branch = run_git(["git", "-C", str(target), "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    source.update({"cache_path": str(target), "commit": commit, "branch": branch, "fetch_status": "success", "error": ""})


def fetch_zip(source: dict, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    archive_path = target / "source.zip"
    extract_dir = target / "extracted"
    urllib.request.urlretrieve(source["input_url"], archive_path)
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extract_dir)
    source.update({"cache_path": str(extract_dir), "commit": "", "branch": "", "fetch_status": "success", "error": ""})


def run_git(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout


def write_fetch_result(path: Path, manifest: dict) -> None:
    lines = [
        "# 代码获取结果",
        "",
        f"- 运行ID：{manifest.get('source_run_id', '')}",
        f"- 获取结果：{'失败' if manifest.get('errors') else '成功'}",
        "",
        "| 服务编号 | 类型 | 名称 | 分支 | Commit | 缓存路径 | 状态 | 问题 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in manifest.get("code_sources", []):
        lines.append(
            f"| {item.get('service_id', '')} | {item.get('source_type', '')} | {item.get('resolved_name', '')} | {item.get('branch', '') or '无'} | {item.get('commit', '') or '无'} | {item.get('cache_path', '') or '无'} | {item.get('fetch_status', '')} | {item.get('error', '') or '无'} |"
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
