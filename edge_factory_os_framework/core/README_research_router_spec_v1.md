# Edge Factory OS Research Router Spec v1

Status: `True`

This router spec defines how future research should be selected through the framework.

## Required order

- load_active_core_manifest
- load_data_quality_guard_feed
- load_lesson_memory
- load_route_blocklist
- load_plugin_configs
- validate_plugin_safety_flags
- validate_plugin_guard_requirements
- route_hash_preflight_against_blocklist
- build_generic_research_contract
- hand_to_generic_runner_framework
- hand_to_generic_evaluator_framework

## Hard blocks

- `DATA_QUALITY_GUARD_NOT_PASS`: guard_pass != True -> block all research routing
- `PLUGIN_SAFETY_FLAG_OPEN`: plugin candidate/family/runtime/capital/live/real_order flag is True -> reject plugin
- `BLOCKED_ROUTE_HASH_REUSE`: route_hash in candidate_route_blocklist -> reject contract
- `CANONICAL_MONTH_POLICY_NOT_12`: canonical_policy_month_count != 12 -> reject research contract
- `MISSING_NEGATIVE_CONTROLS_OR_NULL_MODELS`: plugin lacks negative controls or null models -> diagnostic research not allowed

## Selected plugin

- plugin: `GUARDED_FEATURE_SPACE_EXPANSION_PLUGIN_V1`
- path: `edge_factory_os_framework\plugins\guarded_feature_space_expansion_plugin_v1.json`
- research: `GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH_V1`

## Safety

This spec does not allow candidate generation, family release, runtime touch, capital change, live trading, active paper, or real orders.
