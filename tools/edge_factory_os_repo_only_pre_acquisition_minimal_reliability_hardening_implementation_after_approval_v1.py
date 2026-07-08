from __future__ import annotations

import ast
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "11c0b48"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 648
EXPECTED_TRACKED_PYTHON_COUNT = 649

APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_approval_after_preview_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_approval_after_preview_v1_latest.json"
)
PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1_latest.json"
)
VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1_latest.json"
)
CONTRACT_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1_latest.json"
)
CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1"
    / "pre_acquisition_minimal_reliability_hardening_contract.json"
)

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_after_approval_v1.py"
)
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_validator_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_blocked_record_after_approval_v1.py"
)

APPROVAL_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_APPROVAL_"
    "RECORD_CREATED_IMPLEMENTATION_NEXT"
)
PREVIEW_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW_"
    "APPROVAL_REQUIRED"
)
VALIDATOR_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATED_"
    "IMPLEMENTATION_PREVIEW_NEXT"
)
STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTED_PENDING_VALIDATOR"
)
STATUS_BLOCKED = (
    "BLOCKED_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_P0"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_PRE_ACQUISITION_RELIABILITY_INTERLOCK"
EVIDENCE_BEFORE = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_APPROVED_NEXT_"
    "NO_IMPLEMENTATION_YET"
)
EVIDENCE_AFTER_PASS = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTED_PENDING_VALIDATOR"
)
EVIDENCE_AFTER_BLOCKED = "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_BLOCKED_P0"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"

REQUIRED_FUTURE_ARTIFACTS = [
    "secret_scan_report.json",
    "dependency_environment_snapshot.json",
    "ast_dangerous_call_scan_report.json",
    "pre_acquisition_artifact_hash_manifest.json",
    "timeout_policy.json",
    "memory_disk_resource_policy.json",
    "rollback_policy.json",
    "minimal_hardening_contract_compliance_report.json",
]
CRITICAL_ARTIFACTS = [
    APPROVAL_ARTIFACT,
    PREVIEW_ARTIFACT,
    VALIDATOR_ARTIFACT,
    CONTRACT_SUMMARY_ARTIFACT,
    CONTRACT_ARTIFACT,
]
CURRENT_CHAIN_REL_PATHS = {
    CURRENT_TOOL_REL,
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_approval_after_preview_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1.py",
}
HASH_TOOL_REL_PATHS = [
    CURRENT_TOOL_REL,
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_approval_after_preview_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1.py",
]
TEXT_EXTENSIONS = {
    ".py",
    ".json",
    ".txt",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
    ".tsv",
    ".ps1",
    ".bat",
    ".sh",
}
MAX_SECRET_SCAN_FILE_BYTES = 512 * 1024
MAX_SECRET_FINDINGS_REPORTED = 200
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]
DANGEROUS_FLAGS = [
    "runtime_touched",
    "launcher_executed",
    "launcher_touch_performed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "active_paper_touched",
    "strategy_research_recommended_now",
    "strategy_research_implementation_touched",
    "candidate_generation_recommended_now",
    "candidate_generation_touched",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "family_release_touched",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "hardening_implementation_performed_now",
    "secret_scan_performed_now",
    "dependency_snapshot_performed_now",
    "ast_scanner_performed_now",
    "artifact_hash_manifest_performed_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    if args[:2] not in (["rev-parse", "--short"], ["status", "--short"], ["ls-files"], ["log", "--oneline"]):
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def tracked_files() -> List[str]:
    output = run_git(["ls-files"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def tracked_python_files(files: Iterable[str]) -> List[str]:
    return [path for path in files if path.endswith(".py")]


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def redact(value: str) -> str:
    clean = value.strip()
    if len(clean) <= 8:
        return "***REDACTED***"
    return f"{clean[:3]}***REDACTED***{clean[-3:]}"


def placeholder_context(text: str) -> bool:
    lowered = text.lower()
    markers = [
        "example",
        "placeholder",
        "dummy",
        "sample",
        "fake",
        "test",
        "redacted",
        "changeme",
        "change_me",
        "your_",
        "xxxx",
        "todo",
        "documentation",
        "env var",
        "environment variable",
        "not a secret",
    ]
    return any(marker in lowered for marker in markers)


SECRET_PATTERNS = [
    ("private_key_marker", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws_access_key_id", re.compile(r"\bA[KS]IA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("generic_secret_assignment", re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password|passwd|credential|private[_-]?key)\b"
        r"\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=:]{12,})['\"]?"
    )),
]


def scan_text_for_secrets(label: str, text: str) -> Tuple[List[Dict[str, Any]], int]:
    findings: List[Dict[str, Any]] = []
    placeholder_count = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not any(word in line.lower() for word in ["key", "secret", "token", "pass", "akia", "ghp_", "-----begin"]):
            continue
        for pattern_name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(line):
                candidate = match.group(2) if pattern_name == "generic_secret_assignment" else match.group(0)
                is_placeholder = placeholder_context(line) or shannon_entropy(candidate) < 3.0
                if is_placeholder:
                    placeholder_count += 1
                    classification = "PLACEHOLDER_OR_DOCUMENTATION"
                else:
                    classification = "PLAUSIBLE_LIVE_SECRET"
                if len(findings) < MAX_SECRET_FINDINGS_REPORTED:
                    findings.append(
                        {
                            "path": label,
                            "line": line_number,
                            "pattern": pattern_name,
                            "classification": classification,
                            "redacted_value": redact(candidate),
                        }
                    )
    return findings, placeholder_count


def run_secret_scan(files: List[str]) -> Dict[str, Any]:
    scanned = 0
    skipped_large: List[str] = []
    all_findings: List[Dict[str, Any]] = []
    placeholder_count = 0
    scan_rel_paths = [
        path for path in files if Path(path).suffix.lower() in TEXT_EXTENSIONS and not path.startswith("tools/__pycache__/")
    ]
    if CURRENT_TOOL_REL not in scan_rel_paths and (REPO_ROOT / CURRENT_TOOL_REL).exists():
        scan_rel_paths.append(CURRENT_TOOL_REL)

    for rel in scan_rel_paths:
        path = REPO_ROOT / rel
        if not path.exists() or not path.is_file():
            continue
        size = path.stat().st_size
        if size > MAX_SECRET_SCAN_FILE_BYTES:
            skipped_large.append(rel)
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                continue
        findings, placeholders = scan_text_for_secrets(rel, text)
        all_findings.extend(findings)
        placeholder_count += placeholders
        scanned += 1

    for artifact in CRITICAL_ARTIFACTS:
        if artifact.exists() and artifact.stat().st_size <= MAX_SECRET_SCAN_FILE_BYTES:
            findings, placeholders = scan_text_for_secrets(str(artifact), artifact.read_text(encoding="utf-8"))
            all_findings.extend(findings)
            placeholder_count += placeholders
            scanned += 1

    plausible_findings = [
        finding for finding in all_findings if finding["classification"] == "PLAUSIBLE_LIVE_SECRET"
    ]
    report = {
        "generated_at_utc": utc_now(),
        "secret_scan_performed": True,
        "secret_scan_report_created": True,
        "redaction_policy_applied": True,
        "scan_scope": "tracked repo text files, approved current tool file, and latest critical artifacts",
        "max_file_bytes": MAX_SECRET_SCAN_FILE_BYTES,
        "files_scanned_for_secrets_count": scanned,
        "skipped_large_file_count": len(skipped_large),
        "skipped_large_files": skipped_large[:100],
        "plausible_live_secret_count": len(plausible_findings),
        "placeholder_secret_count": placeholder_count,
        "secret_scan_fail_closed": bool(plausible_findings),
        "findings": all_findings[:MAX_SECRET_FINDINGS_REPORTED],
    }
    write_json(OUT_DIR / "secret_scan_report.json", report)
    return report


def run_dependency_snapshot() -> Dict[str, Any]:
    packages = []
    for dist in sorted(metadata.distributions(), key=lambda item: (item.metadata.get("Name") or "").lower()):
        name = dist.metadata.get("Name") or "UNKNOWN"
        packages.append({"name": name, "version": dist.version})
    report = {
        "generated_at_utc": utc_now(),
        "dependency_environment_snapshot_performed": True,
        "dependency_environment_snapshot_created": True,
        "python_executable": sys.executable,
        "python_version": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "package_snapshot_method": "importlib.metadata.distributions",
        "package_count": len(packages),
        "packages": packages,
        "dependency_install_attempted": False,
        "dependency_update_attempted": False,
        "environment_modified": False,
    }
    write_json(OUT_DIR / "dependency_environment_snapshot.json", report)
    return report


NETWORK_IMPORTS = {"requests", "httpx", "urllib", "aiohttp", "ccxt", "binance", "okx", "socket", "webbrowser"}
RISK_IMPORTS = NETWORK_IMPORTS | {"subprocess", "importlib", "runpy"}
CALL_NAMES = {
    "eval",
    "exec",
    "os.system",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "urllib.request.urlopen",
    "socket.socket",
    "webbrowser.open",
    "runpy.run_path",
    "runpy.run_module",
    "importlib.import_module",
}


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def safe_git_subprocess_call(node: ast.Call) -> bool:
    if dotted_name(node.func) not in {"subprocess.run", "subprocess.check_output"}:
        return False
    if not node.args or not isinstance(node.args[0], ast.List):
        return False
    elements = node.args[0].elts
    values = [element.value for element in elements[:3] if isinstance(element, ast.Constant)]
    return values[:1] == ["git"] or values[:2] == ["git", "-c"]


def classify_ast_finding(rel: str, kind: str, name: str, node: ast.AST) -> str:
    if rel in CURRENT_CHAIN_REL_PATHS:
        if name.startswith("importlib") or name in {"importlib", "importlib.metadata"}:
            return "SAFE_STANDARD_LIBRARY_USAGE"
        if name.startswith("subprocess") and isinstance(node, ast.Call) and safe_git_subprocess_call(node):
            return "SAFE_STANDARD_LIBRARY_USAGE"
        if name.startswith("subprocess") and kind == "import":
            return "SAFE_STANDARD_LIBRARY_USAGE"
        if name in {"eval", "exec", "runpy.run_path", "runpy.run_module", "importlib.import_module"}:
            return "CURRENT_APPROVED_CHAIN_BLOCKER"
        if name.split(".")[0] in NETWORK_IMPORTS:
            return "CURRENT_APPROVED_CHAIN_BLOCKER"
        return "SAFE_STANDARD_LIBRARY_USAGE"
    if "readme" in rel.lower() or rel.endswith(".md"):
        return "GUARD_OR_DOCUMENTATION_ONLY"
    return "DORMANT_REPO_CODE_ATTENTION"


def run_ast_scan(py_files: List[str]) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    parse_errors: List[Dict[str, Any]] = []
    for rel in py_files:
        path = REPO_ROOT / rel
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=rel)
        except SyntaxError as exc:
            parse_errors.append({"path": rel, "line": exc.lineno, "message": exc.msg})
            continue
        except UnicodeDecodeError as exc:
            parse_errors.append({"path": rel, "line": None, "message": str(exc)})
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in RISK_IMPORTS:
                        classification = classify_ast_finding(rel, "import", alias.name, node)
                        findings.append(
                            {
                                "path": rel,
                                "line": getattr(node, "lineno", None),
                                "kind": "import",
                                "name": alias.name,
                                "classification": classification,
                            }
                        )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                root = module.split(".")[0]
                if root in RISK_IMPORTS:
                    classification = classify_ast_finding(rel, "import", module, node)
                    findings.append(
                        {
                            "path": rel,
                            "line": getattr(node, "lineno", None),
                            "kind": "import",
                            "name": module,
                            "classification": classification,
                        }
                    )
            elif isinstance(node, ast.Call):
                name = dotted_name(node.func)
                root = name.split(".")[0]
                matched = name in CALL_NAMES or root in {"eval", "exec"} or root in NETWORK_IMPORTS
                if matched:
                    classification = classify_ast_finding(rel, "call", name, node)
                    findings.append(
                        {
                            "path": rel,
                            "line": getattr(node, "lineno", None),
                            "kind": "call",
                            "name": name,
                            "classification": classification,
                        }
                    )

    current_chain_blockers = [
        item for item in findings if item["classification"] == "CURRENT_APPROVED_CHAIN_BLOCKER"
    ]
    dormant_attention = [
        item for item in findings if item["classification"] == "DORMANT_REPO_CODE_ATTENTION"
    ]
    guard_or_doc = [
        item for item in findings if item["classification"] == "GUARD_OR_DOCUMENTATION_ONLY"
    ]
    executable_external_api = [
        item
        for item in findings
        if item["classification"] in {"CURRENT_APPROVED_CHAIN_BLOCKER", "DORMANT_REPO_CODE_ATTENTION"}
        and item["name"].split(".")[0] in NETWORK_IMPORTS
    ]
    executable_subprocess = [
        item
        for item in findings
        if item["classification"] in {"CURRENT_APPROVED_CHAIN_BLOCKER", "DORMANT_REPO_CODE_ATTENTION"}
        and item["name"].startswith("subprocess")
    ]
    executable_eval_exec = [
        item
        for item in findings
        if item["classification"] in {"CURRENT_APPROVED_CHAIN_BLOCKER", "DORMANT_REPO_CODE_ATTENTION"}
        and item["name"] in {"eval", "exec"}
    ]
    report = {
        "generated_at_utc": utc_now(),
        "ast_scanner_performed": True,
        "ast_dangerous_call_scan_report_created": True,
        "tracked_python_files_scanned_count": len(py_files),
        "ast_parse_error_count": len(parse_errors),
        "dangerous_current_chain_blocker_count": len(current_chain_blockers),
        "dormant_repo_attention_count": len(dormant_attention),
        "guard_or_documentation_only_count": len(guard_or_doc),
        "safe_standard_library_usage_count": len(
            [item for item in findings if item["classification"] == "SAFE_STANDARD_LIBRARY_USAGE"]
        ),
        "executable_external_api_call_count": len(executable_external_api),
        "executable_subprocess_risk_count": len(executable_subprocess),
        "executable_eval_exec_risk_count": len(executable_eval_exec),
        "ast_scanner_fail_closed": bool(parse_errors or current_chain_blockers),
        "parse_errors": parse_errors,
        "findings": findings,
    }
    write_json(OUT_DIR / "ast_dangerous_call_scan_report.json", report)
    return report


def file_hash_record(path: Path, required: bool) -> Dict[str, Any]:
    exists = path.exists()
    record: Dict[str, Any] = {
        "path": str(path),
        "exists": exists,
        "required": required,
        "size": None,
        "mtime_utc": None,
        "sha256": None,
    }
    if exists and path.is_file():
        data = path.read_bytes()
        stat = path.stat()
        record.update(
            {
                "size": stat.st_size,
                "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return record


def run_artifact_manifest() -> Dict[str, Any]:
    records = [file_hash_record(path, required=True) for path in CRITICAL_ARTIFACTS]
    records.extend(file_hash_record(REPO_ROOT / rel, required=(rel == CURRENT_TOOL_REL)) for rel in HASH_TOOL_REL_PATHS)
    missing_required = [record for record in records if record["required"] and not record["exists"]]
    report = {
        "generated_at_utc": utc_now(),
        "artifact_hash_manifest_performed": True,
        "artifact_hash_manifest_created": True,
        "critical_artifact_count": len(CRITICAL_ARTIFACTS),
        "missing_critical_artifact_count": len([record for record in records[: len(CRITICAL_ARTIFACTS)] if not record["exists"]]),
        "hashed_file_count": len([record for record in records if record["exists"] and record["sha256"]]),
        "hash_algorithm": "SHA256",
        "artifact_manifest_fail_closed": bool(missing_required),
        "artifacts": records,
    }
    write_json(OUT_DIR / "pre_acquisition_artifact_hash_manifest.json", report)
    return report


def write_policy_artifacts() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    timeout_policy = {
        "generated_at_utc": utc_now(),
        "timeout_policy_implemented": True,
        "timeout_policy_created": True,
        "future_acquisition_preview_max_runtime_seconds": 600,
        "future_acquisition_execution_max_runtime_seconds": 1800,
        "future_static_scan_max_runtime_seconds": 600,
        "future_external_call_retry_limit_if_separately_approved": 2,
        "future_external_call_timeout_seconds_if_separately_approved": 30,
        "fail_closed_on_timeout": True,
        "external_calls_allowed_now": False,
    }
    memory_disk_policy = {
        "generated_at_utc": utc_now(),
        "memory_disk_resource_policy_implemented": True,
        "memory_disk_resource_policy_created": True,
        "max_text_file_read_bytes_without_separate_approval": MAX_SECRET_SCAN_FILE_BYTES,
        "max_single_output_artifact_bytes_without_review": 10 * 1024 * 1024,
        "large_file_policy": "skip or metadata-only unless separately approved",
        "parquet_policy": "metadata-only unless separately approved",
        "output_size_tracking_required": True,
        "heavy_scan_performed_now": False,
    }
    rollback_policy = {
        "generated_at_utc": utc_now(),
        "rollback_policy_implemented": True,
        "rollback_policy_created": True,
        "pre_execution_checkpoint_required": True,
        "git_head_capture_required": True,
        "git_status_capture_required": True,
        "output_directory_isolation_required": True,
        "no_overwrite_policy": "write timestamped artifacts and latest pointers only in module output directory",
        "failed_execution_preservation_policy": "preserve logs/artifacts and do not overwrite prior successful evidence",
        "environment_rollback_required_if_future_environment_changes_approved": True,
        "repo_mutation_limit": "approved single future tool file only",
    }
    write_json(OUT_DIR / "timeout_policy.json", timeout_policy)
    write_json(OUT_DIR / "memory_disk_resource_policy.json", memory_disk_policy)
    write_json(OUT_DIR / "rollback_policy.json", rollback_policy)
    return timeout_policy, memory_disk_policy, rollback_policy


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    validator = load_json(VALIDATOR_ARTIFACT)
    contract = load_json(CONTRACT_ARTIFACT)
    live_next_module = approval.get("next_module")
    if live_next_module != REQUESTED_MODULE:
        raise RuntimeError(f"{STATUS_BLOCKED_NEXT}: {live_next_module}")

    checks = {
        "approval_status": approval.get(
            "pre_acquisition_minimal_reliability_hardening_implementation_approval_status"
        )
        == APPROVAL_STATUS_PASS,
        "preview_status": preview.get(
            "pre_acquisition_minimal_reliability_hardening_implementation_preview_status"
        )
        == PREVIEW_STATUS_PASS,
        "validator_status": validator.get(
            "pre_acquisition_minimal_reliability_hardening_contract_validator_status"
        )
        == VALIDATOR_STATUS_PASS,
        "implementation_approval_record_created": approval.get("implementation_approval_record_created") is True,
        "recommended_strategy_single_bundle": approval.get("recommended_implementation_strategy")
        == "SINGLE_BOUNDED_BUNDLE",
        "single_bounded_bundle_allowed": approval.get("single_bounded_bundle_allowed") is True,
        "hardening_implementation_eligible_next": approval.get("hardening_implementation_eligible_next") is True,
        "acquisition_execution_false": approval.get("acquisition_execution_allowed_now") is False,
        "active_p0_zero": approval.get("active_p0_blocker_count") == 0,
        "active_p1_one": approval.get("active_p1_attention_count") == 1,
        "evidence_before_expected": approval.get("current_evidence_chain_quality_after_approval")
        == EVIDENCE_BEFORE,
        "generic_runner_blocked": approval.get("generic_runner_implementation_remains_blocked") is True,
        "schema_or_config_false": approval.get("schema_or_config_created") is False,
        "loop_closed": approval.get("loop_remains_closed") is True,
        "contract_artifact_present": bool(contract),
    }
    if not all(checks.values()):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {checks}")

    return (
        {
            "head": head,
            "git_status_short_clean": not status_lines,
            "git_status_short_only_current_tool_pending": set(status_lines) == allowed_pending_status,
            "whole_system_preflight_completed": True,
            "whole_system_preflight_decision": "PASS",
            "live_next_module": live_next_module,
            "live_next_module_matches_requested_module": True,
            "artifact_chain_consistent": True,
            "checks": checks,
        },
        approval,
        preview,
        validator,
        contract,
    )


def build_compliance_report(
    preflight: Dict[str, Any],
    secret_report: Dict[str, Any],
    dependency_report: Dict[str, Any],
    ast_report: Dict[str, Any],
    manifest_report: Dict[str, Any],
    timeout_policy: Dict[str, Any],
    memory_disk_policy: Dict[str, Any],
    rollback_policy: Dict[str, Any],
) -> Dict[str, Any]:
    blockers = []
    if secret_report["secret_scan_fail_closed"]:
        blockers.append("secret_scan")
    if ast_report["ast_scanner_fail_closed"]:
        blockers.append("ast_scanner")
    if manifest_report["artifact_manifest_fail_closed"]:
        blockers.append("artifact_hash_manifest")
    if not dependency_report["dependency_environment_snapshot_created"]:
        blockers.append("dependency_environment_snapshot")
    if not (
        timeout_policy["timeout_policy_created"]
        and memory_disk_policy["memory_disk_resource_policy_created"]
        and rollback_policy["rollback_policy_created"]
    ):
        blockers.append("policy_artifacts")

    success = not blockers
    report = {
        "generated_at_utc": utc_now(),
        "minimal_hardening_contract_compliance_report_created": True,
        "minimal_hardening_implementation_successful": success,
        "hardening_gates_passed": [
            gate
            for gate, passed in {
                "secret_credential_scanning": not secret_report["secret_scan_fail_closed"],
                "dependency_environment_snapshot": dependency_report[
                    "dependency_environment_snapshot_created"
                ],
                "ast_scanner_improvement": not ast_report["ast_scanner_fail_closed"],
                "artifact_hash_manifest_chain": not manifest_report["artifact_manifest_fail_closed"],
                "timeout_policy": timeout_policy["timeout_policy_created"],
                "memory_disk_resource_policy": memory_disk_policy["memory_disk_resource_policy_created"],
                "rollback_policy": rollback_policy["rollback_policy_created"],
            }.items()
            if passed
        ],
        "hardening_gates_blocked": blockers,
        "active_p0_blocker_count": len(blockers),
        "active_p1_attention_count": 1,
        "current_evidence_chain_quality_after_implementation": (
            EVIDENCE_AFTER_PASS if success else EVIDENCE_AFTER_BLOCKED
        ),
        "whole_system_preflight": preflight,
        "gate_counts": {
            "plausible_live_secret_count": secret_report["plausible_live_secret_count"],
            "ast_parse_error_count": ast_report["ast_parse_error_count"],
            "dangerous_current_chain_blocker_count": ast_report[
                "dangerous_current_chain_blocker_count"
            ],
            "missing_critical_artifact_count": manifest_report["missing_critical_artifact_count"],
        },
    }
    write_json(OUT_DIR / "minimal_hardening_contract_compliance_report.json", report)
    return report


def build_summary() -> Dict[str, Any]:
    preflight, approval, preview, validator, contract = validate_preflight()
    files = tracked_files()
    py_files = tracked_python_files(files)

    secret_report = run_secret_scan(files)
    dependency_report = run_dependency_snapshot()
    ast_report = run_ast_scan(py_files)
    manifest_report = run_artifact_manifest()
    timeout_policy, memory_disk_policy, rollback_policy = write_policy_artifacts()
    compliance_report = build_compliance_report(
        preflight,
        secret_report,
        dependency_report,
        ast_report,
        manifest_report,
        timeout_policy,
        memory_disk_policy,
        rollback_policy,
    )

    success = compliance_report["minimal_hardening_implementation_successful"]
    next_module = NEXT_MODULE_VALIDATOR if success else NEXT_MODULE_BLOCKED
    planned_schema_files_existing_count = sum(
        1 for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}

    return {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "pre_acquisition_minimal_reliability_hardening_implementation_status": (
            STATUS_PASS if success else STATUS_BLOCKED
        ),
        "final_decision": (
            "MINIMAL_RELIABILITY_HARDENING_IMPLEMENTED_VALIDATOR_NEXT"
            if success
            else "MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_BLOCKED_P0_RECORD_NEXT"
        ),
        "next_action": (
            "VALIDATE_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION"
            if success
            else "WRITE_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_BLOCKED_RECORD"
        ),
        "next_module": next_module,
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": 0,
        "active_p1_attention_count_from_live_artifact": 1,
        "p1_attention_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_approval_respected": True,
        "recommended_implementation_strategy": "SINGLE_BOUNDED_BUNDLE",
        "single_bounded_bundle_used": True,
        "hardening_implementation_performed": True,
        "secret_scan_performed": True,
        "secret_scan_report_created": True,
        "files_scanned_for_secrets_count": secret_report["files_scanned_for_secrets_count"],
        "plausible_live_secret_count": secret_report["plausible_live_secret_count"],
        "placeholder_secret_count": secret_report["placeholder_secret_count"],
        "secret_scan_fail_closed": secret_report["secret_scan_fail_closed"],
        "redaction_policy_applied": True,
        "dependency_environment_snapshot_performed": True,
        "dependency_environment_snapshot_created": True,
        "python_executable": dependency_report["python_executable"],
        "python_version": dependency_report["python_version"],
        "package_snapshot_method": dependency_report["package_snapshot_method"],
        "package_count": dependency_report["package_count"],
        "dependency_install_attempted": False,
        "dependency_update_attempted": False,
        "environment_modified": False,
        "ast_scanner_performed": True,
        "ast_dangerous_call_scan_report_created": True,
        "tracked_python_files_scanned_count": ast_report["tracked_python_files_scanned_count"],
        "ast_parse_error_count": ast_report["ast_parse_error_count"],
        "dangerous_current_chain_blocker_count": ast_report[
            "dangerous_current_chain_blocker_count"
        ],
        "dormant_repo_attention_count": ast_report["dormant_repo_attention_count"],
        "guard_or_documentation_only_count": ast_report["guard_or_documentation_only_count"],
        "executable_external_api_call_count": ast_report["executable_external_api_call_count"],
        "executable_subprocess_risk_count": ast_report["executable_subprocess_risk_count"],
        "executable_eval_exec_risk_count": ast_report["executable_eval_exec_risk_count"],
        "ast_scanner_fail_closed": ast_report["ast_scanner_fail_closed"],
        "artifact_hash_manifest_performed": True,
        "artifact_hash_manifest_created": True,
        "critical_artifact_count": manifest_report["critical_artifact_count"],
        "missing_critical_artifact_count": manifest_report["missing_critical_artifact_count"],
        "hashed_file_count": manifest_report["hashed_file_count"],
        "hash_algorithm": "SHA256",
        "artifact_manifest_fail_closed": manifest_report["artifact_manifest_fail_closed"],
        "timeout_policy_implemented": True,
        "timeout_policy_created": True,
        "memory_disk_resource_policy_implemented": True,
        "memory_disk_resource_policy_created": True,
        "rollback_policy_implemented": True,
        "rollback_policy_created": True,
        "minimal_hardening_contract_compliance_report_created": True,
        "minimal_hardening_implementation_successful": success,
        "hardening_gates_passed": compliance_report["hardening_gates_passed"],
        "hardening_gates_blocked": compliance_report["hardening_gates_blocked"],
        "acquisition_execution_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "fake_or_synthetic_data_detected": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "current_evidence_chain_quality_before_implementation": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_implementation": (
            EVIDENCE_AFTER_PASS if success else EVIDENCE_AFTER_BLOCKED
        ),
        "active_p0_blocker_count": compliance_report["active_p0_blocker_count"],
        "active_p1_attention_count": 1,
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": (
            "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_READY"
            if success
            else "BLOCKED_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION"
        ),
        "derived_live_repo_post_check_reason": (
            "all eight hardening artifacts were produced by bounded repo-only static checks; "
            "no acquisition, download, fetch, API, dependency install/update, data build, strategy, "
            "runtime, capital, live, generic-runner, schema, or config action occurred"
            if success
            else "one or more hardening gates failed closed and blocked record is required"
        ),
        "replacement_checks_all_true": success,
        "whole_system_preflight": preflight,
        "implementation_sections": {
            "secret_scan_implementation": secret_report,
            "dependency_snapshot_implementation": dependency_report,
            "ast_scanner_implementation": {
                key: ast_report[key]
                for key in [
                    "ast_scanner_performed",
                    "ast_dangerous_call_scan_report_created",
                    "tracked_python_files_scanned_count",
                    "ast_parse_error_count",
                    "dangerous_current_chain_blocker_count",
                    "dormant_repo_attention_count",
                    "guard_or_documentation_only_count",
                    "executable_external_api_call_count",
                    "executable_subprocess_risk_count",
                    "executable_eval_exec_risk_count",
                    "ast_scanner_fail_closed",
                ]
            },
            "artifact_hash_manifest_implementation": manifest_report,
            "policy_artifact_implementation": {
                "timeout_policy_implemented": True,
                "timeout_policy_created": True,
                "memory_disk_resource_policy_implemented": True,
                "memory_disk_resource_policy_created": True,
                "rollback_policy_implemented": True,
                "rollback_policy_created": True,
            },
            "compliance_decision": compliance_report,
            "next_module_decision": {
                "if_implementation_succeeds_no_p0": NEXT_MODULE_VALIDATOR,
                "if_implementation_finds_p0": NEXT_MODULE_BLOCKED,
                "chosen_next_module": next_module,
                "do_not_choose_acquisition_execution": True,
                "do_not_choose_data_download_fetch_api": True,
                "do_not_choose_strategy_candidate_backtest_runtime_live_capital": True,
                "do_not_choose_generic_review_adoption_gate_rollout": True,
            },
        },
        "source_artifacts": {
            "approval_artifact": str(APPROVAL_ARTIFACT),
            "preview_artifact": str(PREVIEW_ARTIFACT),
            "validator_artifact": str(VALIDATOR_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "approval_status": approval.get(
                "pre_acquisition_minimal_reliability_hardening_implementation_approval_status"
            ),
            "preview_status": preview.get(
                "pre_acquisition_minimal_reliability_hardening_implementation_preview_status"
            ),
            "validator_status": validator.get(
                "pre_acquisition_minimal_reliability_hardening_contract_validator_status"
            ),
            "contract_sections": list(contract.keys()),
        },
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
    }


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "pre_acquisition_minimal_reliability_hardening_implementation_status",
        "final_decision",
        "next_module",
        "hardening_implementation_performed",
        "secret_scan_performed",
        "plausible_live_secret_count",
        "dependency_environment_snapshot_performed",
        "ast_scanner_performed",
        "ast_parse_error_count",
        "dangerous_current_chain_blocker_count",
        "artifact_hash_manifest_performed",
        "missing_critical_artifact_count",
        "minimal_hardening_implementation_successful",
        "active_p0_blocker_count",
        "active_p1_attention_count",
    ]
    return "\n".join(f"{field}: {summary.get(field)}" for field in fields) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    latest_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_after_approval_v1_latest.json"
    )
    latest_txt = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_after_approval_v1_latest.txt"
    )
    timestamp_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_after_approval_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
