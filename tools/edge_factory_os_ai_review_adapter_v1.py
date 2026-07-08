from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List


MODULE = "edge_factory_os_ai_review_adapter_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

PACKET_LATEST = (
    BASE_DIR
    / "edge_factory_os_ai_review_packet_builder_v1"
    / "ai_review_packet_latest.json"
)

PROMPT_LATEST = (
    BASE_DIR
    / "edge_factory_os_ai_review_packet_builder_v1"
    / "ai_review_prompt_latest.txt"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"ai_review_adapter_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "ai_review_adapter_latest.json"
LATEST_MD = OUT_ROOT / "ai_review_adapter_latest.md"
LATEST_REVIEW_TXT = OUT_ROOT / "ai_review_latest.txt"


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def rough_token_estimate(text: str) -> int:
    # Conservative rough estimate; actual billing comes from API usage.
    return max(1, int(len(text) / 4))


def extract_output_text(response_obj: Dict[str, Any]) -> str:
    if isinstance(response_obj.get("output_text"), str):
        return response_obj["output_text"]

    chunks: List[str] = []

    output = response_obj.get("output")

    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue

            content = item.get("content")
            if isinstance(content, list):
                for c in content:
                    if not isinstance(c, dict):
                        continue

                    if isinstance(c.get("text"), str):
                        chunks.append(c["text"])

                    if isinstance(c.get("output_text"), str):
                        chunks.append(c["output_text"])

    return "\n".join(chunks).strip()


def call_openai_responses_api(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
    reasoning_effort: str,
    timeout_seconds: int,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_output_tokens": max_output_tokens,
    }

    if reasoning_effort and reasoning_effort.lower() != "none":
        payload["reasoning"] = {
            "effort": reasoning_effort,
        }

    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    with urllib.request.urlopen(request, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")
        return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Edge Factory OS AI Review Adapter v1")

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually call the API. Without this flag, adapter runs dry-run only.",
    )

    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai"],
        help="AI provider. v1 supports OpenAI only.",
    )

    parser.add_argument(
        "--model",
        default="gpt-5.4-mini",
        help="Model name.",
    )

    parser.add_argument(
        "--reasoning_effort",
        default="low",
        help="Reasoning effort, for example none/low/medium/high depending on model support.",
    )

    parser.add_argument(
        "--max_output_tokens",
        type=int,
        default=1800,
        help="Hard output-token cap for cost control.",
    )

    parser.add_argument(
        "--max_estimated_input_tokens",
        type=int,
        default=30000,
        help="Block call if rough prompt token estimate exceeds this.",
    )

    parser.add_argument(
        "--timeout_seconds",
        type=int,
        default=120,
        help="HTTP timeout.",
    )

    args = parser.parse_args()

    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    packet_state = load_json(PACKET_LATEST)
    prompt = read_text(PROMPT_LATEST)

    if packet_state is None:
        critical.append(f"missing_packet_json:{PACKET_LATEST}")

    if not prompt.strip():
        critical.append(f"missing_prompt_text:{PROMPT_LATEST}")

    packet_status = None
    packet_reason = None

    if packet_state:
        packet_status = packet_state.get("packet_status")
        packet_reason = packet_state.get("reason")

    estimated_input_tokens = rough_token_estimate(prompt)
    estimated_output_token_cap = args.max_output_tokens

    if estimated_input_tokens > args.max_estimated_input_tokens:
        critical.append(
            f"estimated_input_tokens_too_high:{estimated_input_tokens}>{args.max_estimated_input_tokens}"
        )

    api_key_present = bool(os.environ.get("OPENAI_API_KEY"))

    api_call_performed = False
    api_call_allowed = bool(args.execute and not critical)
    api_response: Optional[Dict[str, Any]] = None
    review_text = ""
    api_error = None

    if not args.execute:
        adapter_status = "AI_REVIEW_ADAPTER_DRY_RUN_READY"
        severity = "INFO"
        next_action = "SET_OPENAI_API_KEY_AND_RERUN_WITH_EXECUTE_IF_YOU_WANT_MODEL_REVIEW"
        reason = "dry_run_only; no api call performed"

    elif not api_key_present:
        adapter_status = "AI_REVIEW_ADAPTER_WAIT_API_KEY"
        severity = "ATTENTION"
        next_action = "SET_OPENAI_API_KEY_ENV_VAR_THEN_RERUN_WITH_EXECUTE"
        reason = "OPENAI_API_KEY environment variable not found"
        attention.append("api_key_missing")

    elif critical:
        adapter_status = "AI_REVIEW_ADAPTER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        next_action = "FIX_PACKET_OR_PROMPT_INPUTS"
        reason = "; ".join(critical)

    else:
        try:
            api_response = call_openai_responses_api(
                api_key=os.environ["OPENAI_API_KEY"],
                model=args.model,
                prompt=prompt,
                max_output_tokens=args.max_output_tokens,
                reasoning_effort=args.reasoning_effort,
                timeout_seconds=args.timeout_seconds,
            )
            api_call_performed = True
            review_text = extract_output_text(api_response)

            if review_text:
                adapter_status = "AI_REVIEW_ADAPTER_REVIEW_RECEIVED"
                severity = "ATTENTION"
                next_action = "SAVE_REVIEW_AND_OPTIONALLY_BUILD_OFFLINE_RESEARCH_CONTRACTS"
                reason = "model_review_received; advisory_only"
            else:
                adapter_status = "AI_REVIEW_ADAPTER_EMPTY_REVIEW"
                severity = "ATTENTION"
                next_action = "INSPECT_API_RESPONSE"
                reason = "api returned but no output_text extracted"

        except urllib.error.HTTPError as e:
            try:
                api_error = e.read().decode("utf-8", errors="ignore")
            except Exception:
                api_error = repr(e)

            adapter_status = "AI_REVIEW_ADAPTER_API_HTTP_ERROR"
            severity = "ATTENTION"
            next_action = "INSPECT_API_ERROR_AND_MODEL_NAME_OR_BILLING"
            reason = f"http_error:{e.code}"
            attention.append(api_error)

        except Exception as e:
            api_error = repr(e)
            adapter_status = "AI_REVIEW_ADAPTER_API_ERROR"
            severity = "ATTENTION"
            next_action = "INSPECT_API_ERROR"
            reason = api_error
            attention.append(api_error)

    # Never store or print the API key.
    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "adapter_status": adapter_status,
        "severity": severity,
        "next_action": next_action,
        "reason": reason,

        "provider": args.provider,
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "max_output_tokens": args.max_output_tokens,
        "max_estimated_input_tokens": args.max_estimated_input_tokens,
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_output_token_cap": estimated_output_token_cap,

        "packet_source": str(PACKET_LATEST),
        "prompt_source": str(PROMPT_LATEST),
        "packet_status": packet_status,
        "packet_reason": packet_reason,

        "api_key_present": api_key_present,
        "api_call_requested": bool(args.execute),
        "api_call_allowed": api_call_allowed,
        "api_call_performed": api_call_performed,
        "api_error": api_error,

        "review_text": review_text,
        "raw_api_response_saved": bool(api_response),

        "api_usage": api_response.get("usage") if isinstance(api_response, dict) else None,
        "api_response_id": api_response.get("id") if isinstance(api_response, dict) else None,
        "api_response_status": api_response.get("status") if isinstance(api_response, dict) else None,

        "safety_contract": {
            "runtime_mutation_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
            "advisory_only": True,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "ai_review_adapter_v1_state.json"
    out_md = RUN_DIR / "ai_review_adapter_v1_report.md"
    out_review = RUN_DIR / "ai_review_v1.txt"
    out_raw_response = RUN_DIR / "openai_raw_response_v1.json"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    if api_response is not None:
        dump_json(out_raw_response, api_response)

    out_review.write_text(review_text, encoding="utf-8")
    LATEST_REVIEW_TXT.write_text(review_text, encoding="utf-8")

    md = f"""# EDGE FACTORY OS AI REVIEW ADAPTER v1

adapter_status: {adapter_status}  
severity: {severity}  
next_action: {next_action}  
reason: {reason}

provider: {args.provider}  
model: {args.model}  
reasoning_effort: {args.reasoning_effort}  
estimated_input_tokens: {estimated_input_tokens}  
max_output_tokens: {args.max_output_tokens}

packet_status: {packet_status}  
api_key_present: {api_key_present}  
api_call_requested: {bool(args.execute)}  
api_call_performed: {api_call_performed}  
api_response_status: {result.get("api_response_status")}  
api_usage: {result.get("api_usage")}

review_path: {LATEST_REVIEW_TXT}

## Review Text

{review_text[:12000] if review_text else ""}

## Safety

runtime_mutation_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: False  
advisory_only: True

critical: {critical}  
attention: {attention}  
info: {info}
"""
    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS AI REVIEW ADAPTER v1")
    print("=" * 100)
    print(f"adapter_status: {adapter_status}")
    print(f"severity: {severity}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("MODEL / COST GUARD")
    print("-" * 100)
    print(f"provider: {args.provider}")
    print(f"model: {args.model}")
    print(f"reasoning_effort: {args.reasoning_effort}")
    print(f"estimated_input_tokens: {estimated_input_tokens}")
    print(f"max_estimated_input_tokens: {args.max_estimated_input_tokens}")
    print(f"max_output_tokens: {args.max_output_tokens}")
    print()
    print("API")
    print("-" * 100)
    print(f"api_key_present: {api_key_present}")
    print(f"api_call_requested: {bool(args.execute)}")
    print(f"api_call_performed: {api_call_performed}")
    print(f"api_response_status: {result.get('api_response_status')}")
    print(f"api_usage: {result.get('api_usage')}")
    if api_error:
        print(f"api_error: {api_error[:1000]}")
    print()
    print("SAFETY")
    print("-" * 100)
    print("runtime_mutation_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print("advisory_only: True")
    print()
    if review_text:
        print("REVIEW PREVIEW")
        print("-" * 100)
        print(review_text[:3000])
        print()
    print(f"latest_json: {LATEST_JSON}")
    print(f"latest_review: {LATEST_REVIEW_TXT}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
