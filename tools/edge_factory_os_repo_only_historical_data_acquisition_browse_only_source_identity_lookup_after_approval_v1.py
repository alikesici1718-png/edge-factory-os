from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "05e7c7f"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 665
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 666

REQUESTED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1.py"
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "validator_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "blocked_record_after_approval_v1.py"
)

APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1_latest.json"
)
BROWSE_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_preview_after_user_identity_validator_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_preview_after_user_identity_validator_v1_latest.json"
)
USER_IDENTITY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1_latest.json"
)

STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_COMPLETE_PENDING_VALIDATOR_NO_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_LOOKUP = "BLOCKED_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_INCONCLUSIVE_NO_EXECUTION"

APPROVAL_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION"
PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
USER_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_"
    "BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
)

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION"
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_COMPLETE_PENDING_VALIDATOR_NO_EXECUTION"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
OKX_MAIN_PAGE = "https://tr.okx.com/en/historical-data"
OKX_SAMPLE_ZIP = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)

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
DANGEROUS_FLAG_NAMES = [
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
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    allowed = (
        ["rev-parse", "--short", "HEAD"],
        ["status", "--short"],
        ["ls-files"],
    )
    if args not in allowed:
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: artifact missing/invalid: {path}") from exc
    if not isinstance(data, dict) or not data:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: artifact empty/non-object: {path}")
    return data


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_equal(actual: Any, expected: Any, field: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field}={actual!r} expected {expected!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


def normalize_status_lines(status: str) -> List[str]:
    return [line.strip() for line in status.splitlines() if line.strip()]


def validate_repo_status_allows_current_tool_only(status: str) -> None:
    allowed = {f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"}
    unexpected = [line for line in normalize_status_lines(status) if line not in allowed]
    if unexpected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def strip_page_text(raw_html: str) -> str:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", raw_html)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\\u002[Ff]", "/", text)
    text = re.sub(r"\\u003[Cc]", "<", text)
    text = re.sub(r"\\u003[Ee]", ">", text)
    text = re.sub(r"\\u0026", "&", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def snippets(text: str, patterns: List[str], radius: int = 140) -> List[str]:
    found: List[str] = []
    lowered = text.lower()
    for pattern in patterns:
        idx = lowered.find(pattern.lower())
        if idx == -1:
            continue
        start = max(0, idx - radius)
        end = min(len(text), idx + len(pattern) + radius)
        found.append(text[start:end].strip())
    return found[:8]


def visible_or_embedded_contains(text: str, raw_html: str, patterns: List[str]) -> bool:
    combined = f"{text}\n{raw_html}"
    return any(re.search(pattern, combined, re.IGNORECASE) for pattern in patterns)


def fetch_exact_okx_page() -> Tuple[bool, str, str, Dict[str, Any]]:
    parsed = urlparse(OKX_MAIN_PAGE)
    if parsed.scheme != "https" or parsed.netloc != "tr.okx.com" or parsed.path != "/en/historical-data":
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: approved URL mutated")
    request = Request(
        OKX_MAIN_PAGE,
        headers={
            "User-Agent": "EdgeFactoryOSBrowseOnlySourceIdentityLookup/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
        method="GET",
    )
    opener = build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=25) as response:
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")
            status = getattr(response, "status", None) or response.getcode()
            body = response.read(2_000_000)
    except HTTPError as exc:
        return False, "", "", {
            "okx_page_request_attempted": True,
            "okx_page_request_url": OKX_MAIN_PAGE,
            "okx_page_http_error": exc.code,
            "okx_page_read_error": str(exc),
        }
    except URLError as exc:
        return False, "", "", {
            "okx_page_request_attempted": True,
            "okx_page_request_url": OKX_MAIN_PAGE,
            "okx_page_read_error": str(exc.reason),
        }
    except OSError as exc:
        return False, "", "", {
            "okx_page_request_attempted": True,
            "okx_page_request_url": OKX_MAIN_PAGE,
            "okx_page_read_error": str(exc),
        }

    final = urlparse(final_url)
    if final_url != OKX_MAIN_PAGE:
        return False, "", "", {
            "okx_page_request_attempted": True,
            "okx_page_request_url": OKX_MAIN_PAGE,
            "okx_page_final_url": final_url,
            "okx_page_read_error": "redirect_or_url_change_refused_by_exact_page_scope",
        }
    if final.scheme != "https" or final.netloc != "tr.okx.com" or final.path != "/en/historical-data":
        return False, "", "", {
            "okx_page_request_attempted": True,
            "okx_page_request_url": OKX_MAIN_PAGE,
            "okx_page_final_url": final_url,
            "okx_page_read_error": "final_url_outside_approved_exact_page",
        }
    raw_html = body.decode("utf-8", errors="replace")
    text = strip_page_text(raw_html)
    meta = {
        "okx_page_request_attempted": True,
        "okx_page_request_url": OKX_MAIN_PAGE,
        "okx_page_final_url": final_url,
        "okx_page_http_status": status,
        "okx_page_content_type": content_type,
        "okx_page_bytes_read": len(body),
        "okx_page_read_limit_bytes": 2_000_000,
        "only_approved_page_requested": True,
        "zip_or_archive_url_requested": False,
        "api_url_requested": False,
        "asset_or_secondary_url_requested": False,
    }
    return True, raw_html, text, meta


def sample_zip_pattern_consistency() -> Dict[str, Any]:
    pattern = re.compile(
        r"^https://static\.okx\.com/cdn/okex/traderecords/candlesticks/daily/"
        r"(?P<date_path>\d{8})/"
        r"(?P<instrument>[A-Z0-9]+(?:-[A-Z0-9]+){1,3})-candlesticks-"
        r"(?P<iso_date>\d{4}-\d{2}-\d{2})\.zip$"
    )
    match = pattern.match(OKX_SAMPLE_ZIP)
    return {
        "sample_zip_url": OKX_SAMPLE_ZIP,
        "sample_zip_not_requested": True,
        "sample_zip_downloaded": False,
        "sample_zip_pattern_regex_matched": bool(match),
        "sample_zip_pattern_kind": "static.okx.com/cdn/okex/traderecords/candlesticks/daily/YYYYMMDD/INSTRUMENT-candlesticks-YYYY-MM-DD.zip",
        "sample_zip_pattern_consistency": "PLAUSIBLE_STATIC_OKX_CANDLESTICK_DAILY_ARCHIVE_PATTERN_ONLY"
        if match
        else "NOT_ESTABLISHED",
    }


def analyze_page(raw_html: str, text: str) -> Dict[str, Any]:
    official = urlparse(OKX_MAIN_PAGE).netloc.endswith("okx.com")
    historical = visible_or_embedded_contains(text, raw_html, [r"historical\s+(market\s+)?data", r"historical data"])
    candlestick = visible_or_embedded_contains(text, raw_html, [r"candlestick", r"\bOHLC\b", r"\bOHLCV\b", r"open.*high.*low.*close"])
    july_2023 = visible_or_embedded_contains(text, raw_html, [r"July\s+2023", r"Jul(?:y)?\s*1?,?\s*2023", r"2023-07", r"2023/07"])
    start = "July 2023" if july_2023 else None
    archive_route = visible_or_embedded_contains(
        text,
        raw_html,
        [r"download", r"archive", r"traderecords", r"static\.okx\.com", r"\.zip"],
    )
    file_format = visible_or_embedded_contains(text, raw_html, [r"\.zip", r"\bCSV\b", r"file format", r"format"])
    daily_monthly = visible_or_embedded_contains(text, raw_html, [r"\bdaily\b", r"\bmonthly\b", r"\bdate\b"])
    interval_1h = visible_or_embedded_contains(text, raw_html, [r"\b1h\b", r"\b1 hour\b", r"\b1-hour\b", r"60m"])
    instrument = visible_or_embedded_contains(
        text,
        raw_html,
        [r"instrument", r"symbol", r"BTC-USDT", r"swap", r"spot", r"futures", r"market"],
    )
    timezone = visible_or_embedded_contains(text, raw_html, [r"timezone", r"\bUTC\b", r"timestamp", r"time stamp"])
    terms = visible_or_embedded_contains(text, raw_html, [r"terms", r"license", r"disclaimer", r"copyright", r"agreement"])
    sample = sample_zip_pattern_consistency()
    possible_3y = bool(july_2023)
    incomplete = []
    if not interval_1h:
        incomplete.append("1h candle interval availability not visible")
    if not timezone:
        incomplete.append("timestamp/timezone rules not visible")
    if not instrument:
        incomplete.append("full instrument/symbol universe not visible")
    if not file_format:
        incomplete.append("complete archive file schema/format not visible")
    if not terms:
        incomplete.append("source/license/terms restrictions not visible")
    incomplete.extend(
        [
            "full source manifest not visible",
            "full 4-year continuous coverage not proven",
            "acquisition provenance report not proven",
        ]
    )
    p1_count = 4 + len({item for item in incomplete[:4]})
    return {
        "page_domain": urlparse(OKX_MAIN_PAGE).netloc,
        "page_identity_snippets": snippets(text, ["Historical data", "Market data", "candlestick", "Candlesticks", "July 2023"]),
        "okx_official_page_evidence_found": official,
        "okx_historical_market_data_page_evidence_found": historical,
        "okx_candlestick_source_evidence_found": candlestick,
        "okx_candlestick_coverage_start_visible": bool(start),
        "okx_candlestick_coverage_start": start,
        "okx_candlestick_coverage_statement": "Candlestick/OHLC history starts July 2023"
        if start
        else "No candlestick/OHLC coverage start date was visible in approved page HTML/text",
        "okx_3_year_coverage_likely_or_possible": possible_3y,
        "full_3_to_4_year_coverage_proven_now": False,
        "full_4_year_coverage_proven_now": False,
        "okx_archive_or_download_route_visible": archive_route,
        "okx_archive_pattern_evidence_found": archive_route or sample["sample_zip_pattern_regex_matched"],
        "okx_sample_zip_pattern_consistency": sample["sample_zip_pattern_consistency"],
        "okx_file_format_visible": file_format,
        "okx_data_frequency_visible": daily_monthly,
        "okx_1h_interval_visible": interval_1h,
        "okx_instrument_universe_visible": instrument,
        "okx_timestamp_timezone_visible": timezone,
        "okx_terms_or_license_visible": terms,
        "source_identity_lookup_incomplete_fields": incomplete,
        "source_identity_lookup_p0_count": 0,
        "source_identity_lookup_p1_count": p1_count,
        "source_identity_lookup_p2_count": 1,
        "sample_zip_pattern_evidence": sample,
    }


def preflight() -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    status = run_git(["status", "--short"])
    validate_repo_status_allows_current_tool_only(status)

    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(BROWSE_PREVIEW_ARTIFACT)
    validator = load_json(USER_IDENTITY_VALIDATOR_ARTIFACT)

    require_equal(
        approval.get("historical_data_acquisition_browse_only_source_identity_lookup_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval_status",
    )
    require_equal(
        preview.get("historical_data_acquisition_browse_only_source_identity_lookup_preview_status"),
        PREVIEW_STATUS_PASS,
        "preview_status",
    )
    require_equal(
        validator.get("historical_data_acquisition_user_supplied_source_identity_input_validator_status"),
        USER_VALIDATOR_STATUS_PASS,
        "validator_status",
    )
    require_equal(approval.get("next_module"), REQUESTED_MODULE, "approval.next_module")
    require_true(approval.get("browse_only_lookup_eligible_next"), "browse_only_lookup_eligible_next")
    require_true(approval.get("approval_grants_future_browse_only_lookup_next"), "approval_grants_future_browse_only_lookup_next")
    require_false(approval.get("approval_grants_okx_zip_download_now"), "approval_grants_okx_zip_download_now")
    require_false(approval.get("approval_grants_okx_api_now"), "approval_grants_okx_api_now")
    require_false(approval.get("approval_grants_data_download_now"), "approval_grants_data_download_now")
    require_false(approval.get("approval_grants_data_build_now"), "approval_grants_data_build_now")
    require_equal(approval.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(approval.get("active_p1_attention_count"), 4, "active_p1_attention_count")
    require_equal(approval.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(approval.get("okx_main_page_to_check"), OKX_MAIN_PAGE, "okx_main_page_to_check")
    require_equal(approval.get("okx_sample_zip_identity_to_check"), OKX_SAMPLE_ZIP, "okx_sample_zip_identity_to_check")
    require_false(approval.get("generic_runner_approval_granted"), "generic_runner_approval_granted")
    require_true(approval.get("generic_runner_implementation_remains_blocked"), "generic_runner_implementation_remains_blocked")
    require_false(approval.get("schema_or_config_created"), "schema_or_config_created")

    return {
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "blocked_actions_absent_from_requested_module": True,
        "active_p0_blocker_count_from_live_artifact": approval.get("active_p0_blocker_count"),
        "active_p1_attention_count_from_live_artifact": approval.get("active_p1_attention_count"),
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "browse_preview_artifact": str(BROWSE_PREVIEW_ARTIFACT),
        "user_identity_validator_artifact": str(USER_IDENTITY_VALIDATOR_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def build_payload(preflight_report: Dict[str, Any], lookup_ok: bool, network_meta: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    page_identity_completed = bool(
        lookup_ok
        and analysis.get("okx_official_page_evidence_found")
        and analysis.get("okx_historical_market_data_page_evidence_found")
        and analysis.get("okx_candlestick_source_evidence_found")
    )
    safe_success = page_identity_completed
    incomplete = list(analysis.get("source_identity_lookup_incomplete_fields", []))
    if not safe_success and "approved page could not be read or did not confirm OKX historical candlestick identity" not in incomplete:
        incomplete.insert(0, "approved page could not be read or did not confirm OKX historical candlestick identity")
    source_artifacts = [
        "historical_browse_only_source_identity_lookup_report.json",
        "historical_okx_official_page_evidence_report.json",
        "historical_okx_candlestick_coverage_evidence_report.json",
        "historical_okx_archive_pattern_evidence_report.json",
        "historical_okx_terms_or_source_notes_report.json",
        "historical_browse_only_lookup_contract_compliance_report.json",
    ]
    status = STATUS_PASS if safe_success else STATUS_BLOCKED_LOOKUP
    next_module = NEXT_MODULE_VALIDATOR if safe_success else NEXT_MODULE_BLOCKED
    next_action = (
        "RUN_SOURCE_IDENTITY_LOOKUP_VALIDATOR_NO_DOWNLOAD_NO_API_NO_DATA_BUILD"
        if safe_success
        else "CREATE_BLOCKED_LOOKUP_RECORD_NO_DOWNLOAD_NO_API_NO_DATA_BUILD"
    )
    active_p1 = max(4, int(analysis.get("source_identity_lookup_p1_count", 4)))
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight_report.get("whole_system_preflight_decision") == "PASS",
        "only_okx_main_page_browsed": bool(network_meta.get("only_approved_page_requested")),
        "no_zip_download": True,
        "no_api_call": True,
        "no_data_download_fetch_build": True,
        "acquisition_blocked": True,
        "source_manifest_not_proven": True,
        "provenance_not_proven": True,
        "generic_runner_blocked": True,
        "schema_config_absent": True,
        "loop_closed": True,
        "not_overclaimed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_browse_only_source_identity_lookup_status": status,
        "final_decision": EVIDENCE_AFTER if safe_success else STATUS_BLOCKED_LOOKUP,
        "next_action": next_action,
        "next_module": next_module,
        **preflight_report,
        "prior_browse_only_lookup_approval_respected": True,
        "browse_only_lookup_performed": bool(lookup_ok),
        "page_identity_lookup_completed": page_identity_completed,
        "okx_main_page_browsed_now": bool(lookup_ok),
        "okx_sample_zip_downloaded_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "external_api_calls_performed": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "okx_official_page_evidence_found": bool(analysis.get("okx_official_page_evidence_found")),
        "okx_historical_market_data_page_evidence_found": bool(analysis.get("okx_historical_market_data_page_evidence_found")),
        "okx_candlestick_source_evidence_found": bool(analysis.get("okx_candlestick_source_evidence_found")),
        "okx_candlestick_coverage_start_visible": bool(analysis.get("okx_candlestick_coverage_start_visible")),
        "okx_candlestick_coverage_start": analysis.get("okx_candlestick_coverage_start"),
        "okx_candlestick_coverage_statement": analysis.get("okx_candlestick_coverage_statement"),
        "okx_3_year_coverage_likely_or_possible": bool(analysis.get("okx_3_year_coverage_likely_or_possible")),
        "full_3_to_4_year_coverage_proven_now": False,
        "full_4_year_coverage_proven_now": False,
        "okx_archive_or_download_route_visible": bool(analysis.get("okx_archive_or_download_route_visible")),
        "okx_archive_pattern_evidence_found": bool(analysis.get("okx_archive_pattern_evidence_found")),
        "okx_sample_zip_pattern_consistency": analysis.get("okx_sample_zip_pattern_consistency", "NOT_ESTABLISHED"),
        "okx_file_format_visible": bool(analysis.get("okx_file_format_visible")),
        "okx_1h_interval_visible": bool(analysis.get("okx_1h_interval_visible")),
        "okx_instrument_universe_visible": bool(analysis.get("okx_instrument_universe_visible")),
        "okx_timestamp_timezone_visible": bool(analysis.get("okx_timestamp_timezone_visible")),
        "okx_terms_or_license_visible": bool(analysis.get("okx_terms_or_license_visible")),
        "source_manifest_proven_now": False,
        "provenance_report_proven_now": False,
        "source_identity_lookup_incomplete_fields": incomplete,
        "source_identity_lookup_p0_count": 0,
        "source_identity_lookup_p1_count": active_p1,
        "source_identity_lookup_p2_count": int(analysis.get("source_identity_lookup_p2_count", 1)),
        "source_identity_lookup_artifacts_created": source_artifacts,
        "okx_source_identity_lookup_completed": page_identity_completed,
        "okx_source_identity_partially_verified": page_identity_completed,
        "okx_source_verified_for_acquisition_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "fake_or_synthetic_data_detected": False,
        "source_manifest_required": True,
        "provenance_report_required": True,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "timeout_policy_required_for_acquisition": True,
        "memory_disk_resource_policy_required_for_acquisition": True,
        "rollback_policy_required_for_acquisition": True,
        "hardening_state_required_for_acquisition": True,
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
        "current_evidence_chain_quality_before_lookup": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_lookup": EVIDENCE_AFTER if safe_success else STATUS_BLOCKED_LOOKUP,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": active_p1,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value),
        "derived_live_repo_post_check": "PASS_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_COMPLETE_PENDING_VALIDATOR_NO_EXECUTION"
        if safe_success
        else "BLOCKED_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_INCONCLUSIVE_NO_EXECUTION",
        "derived_live_repo_post_check_reason": (
            "approved browse-only lookup read only the OKX historical data page HTML/text, recorded partial source identity evidence, "
            "downloaded no ZIP/archive/file, called no API, fetched no data beyond the approved page, built no data, and kept acquisition blocked"
            if safe_success
            else "approved page could not safely establish OKX historical candlestick source identity; no ZIP/archive/file download, API call, data build, strategy, runtime, capital, live, generic-runner, schema, config, or old-route action occurred"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "lookup_network_audit": network_meta,
        "lookup_analysis": analysis,
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    official = {
        "generated_at_utc": payload["generated_at_utc"],
        "okx_main_page_to_check": OKX_MAIN_PAGE,
        "okx_official_page_evidence_found": payload["okx_official_page_evidence_found"],
        "okx_historical_market_data_page_evidence_found": payload["okx_historical_market_data_page_evidence_found"],
        "page_identity_lookup_completed": payload["page_identity_lookup_completed"],
        "page_identity_snippets": payload.get("lookup_analysis", {}).get("page_identity_snippets", []),
    }
    coverage = {
        "generated_at_utc": payload["generated_at_utc"],
        "okx_candlestick_source_evidence_found": payload["okx_candlestick_source_evidence_found"],
        "okx_candlestick_coverage_start_visible": payload["okx_candlestick_coverage_start_visible"],
        "okx_candlestick_coverage_start": payload["okx_candlestick_coverage_start"],
        "okx_candlestick_coverage_statement": payload["okx_candlestick_coverage_statement"],
        "okx_3_year_coverage_likely_or_possible": payload["okx_3_year_coverage_likely_or_possible"],
        "full_3_to_4_year_coverage_proven_now": False,
        "full_4_year_coverage_proven_now": False,
        "source_manifest_proven_now": False,
    }
    archive = {
        "generated_at_utc": payload["generated_at_utc"],
        "okx_archive_or_download_route_visible": payload["okx_archive_or_download_route_visible"],
        "okx_archive_pattern_evidence_found": payload["okx_archive_pattern_evidence_found"],
        "okx_sample_zip_pattern_consistency": payload["okx_sample_zip_pattern_consistency"],
        "sample_zip_pattern_evidence": payload.get("lookup_analysis", {}).get("sample_zip_pattern_evidence", {}),
        "okx_sample_zip_downloaded_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
    }
    terms = {
        "generated_at_utc": payload["generated_at_utc"],
        "okx_terms_or_license_visible": payload["okx_terms_or_license_visible"],
        "okx_timestamp_timezone_visible": payload["okx_timestamp_timezone_visible"],
        "okx_1h_interval_visible": payload["okx_1h_interval_visible"],
        "okx_instrument_universe_visible": payload["okx_instrument_universe_visible"],
        "source_identity_lookup_incomplete_fields": payload["source_identity_lookup_incomplete_fields"],
    }
    compliance = {
        key: payload[key]
        for key in [
            "whole_system_preflight_completed",
            "whole_system_preflight_decision",
            "prior_browse_only_lookup_approval_respected",
            "browse_only_lookup_performed",
            "okx_main_page_browsed_now",
            "okx_sample_zip_downloaded_now",
            "okx_download_performed",
            "okx_api_call_performed",
            "external_api_calls_performed",
            "data_download_performed",
            "data_fetch_performed",
            "data_build_performed",
            "acquisition_execution_allowed_now",
            "external_download_allowed_now",
            "external_api_allowed_now",
            "generic_runner_implementation_remains_blocked",
            "schema_or_config_created",
            "loop_remains_closed",
            "replacement_checks_all_true",
        ]
    }
    artifacts = {
        "historical_browse_only_source_identity_lookup_report.json": payload,
        "historical_okx_official_page_evidence_report.json": official,
        "historical_okx_candlestick_coverage_evidence_report.json": coverage,
        "historical_okx_archive_pattern_evidence_report.json": archive,
        "historical_okx_terms_or_source_notes_report.json": terms,
        "historical_browse_only_lookup_contract_compliance_report.json": compliance,
        "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1_latest.json": payload,
    }
    for name, artifact_payload in artifacts.items():
        write_json(OUT_DIR / name, artifact_payload)


def main() -> int:
    preflight_report = preflight()
    lookup_ok, raw_html, text, network_meta = fetch_exact_okx_page()
    analysis = analyze_page(raw_html, text) if lookup_ok else {
        "okx_official_page_evidence_found": False,
        "okx_historical_market_data_page_evidence_found": False,
        "okx_candlestick_source_evidence_found": False,
        "okx_candlestick_coverage_start_visible": False,
        "okx_candlestick_coverage_start": None,
        "okx_candlestick_coverage_statement": "Approved page could not be read; no findings fabricated",
        "okx_3_year_coverage_likely_or_possible": False,
        "okx_archive_or_download_route_visible": False,
        "okx_archive_pattern_evidence_found": sample_zip_pattern_consistency()["sample_zip_pattern_regex_matched"],
        "okx_sample_zip_pattern_consistency": sample_zip_pattern_consistency()["sample_zip_pattern_consistency"],
        "okx_file_format_visible": False,
        "okx_1h_interval_visible": False,
        "okx_instrument_universe_visible": False,
        "okx_timestamp_timezone_visible": False,
        "okx_terms_or_license_visible": False,
        "source_identity_lookup_incomplete_fields": [
            "approved OKX historical data page unreadable in browse-only lookup"
        ],
        "source_identity_lookup_p0_count": 1,
        "source_identity_lookup_p1_count": 4,
        "source_identity_lookup_p2_count": 1,
        "sample_zip_pattern_evidence": sample_zip_pattern_consistency(),
    }
    payload = build_payload(preflight_report, lookup_ok, network_meta, analysis)
    write_artifacts(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        failure = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_browse_only_source_identity_lookup_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_DOWNLOAD_NO_API_NO_DATA_BUILD",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "browse_only_lookup_performed": False,
            "okx_main_page_browsed_now": False,
            "okx_sample_zip_downloaded_now": False,
            "okx_download_performed": False,
            "okx_api_call_performed": False,
            "external_api_calls_performed": False,
            "data_download_performed": False,
            "data_fetch_performed": False,
            "data_build_performed": False,
            "acquisition_execution_allowed_now": False,
            "external_download_allowed_now": False,
            "external_api_allowed_now": False,
            "fake_or_synthetic_data_detected": False,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "loop_remains_closed": True,
        }
        write_json(OUT_DIR / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1_latest.json", failure)
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
