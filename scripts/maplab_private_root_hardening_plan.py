#!/usr/bin/env python3
"""Validate the MAPLAB private-root and deployed-readback hardening plan.

This program is intentionally a static, no-network planner.  It inventories
source-level consumers and local file modes, exercises generated policy-gate
predicates (not resolver/copy-ledger runtime), and writes only a hash-safe
owner-only receipt.  It
does not chmod, copy, move, restart, or deploy any live target; call Google;
inspect customer rows; or read credential/environment payloads.  Receipt-only
permission and atomic-write operations are recorded separately, and secret
values are never emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import stat
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "maplab.margin.private-root-readback-plan-receipt.v1"
METHOD_VERSION = "margin-private-root-deployed-readback-plan-v1"
EXPECTED_CREATED_AT = "2026-08-27T23:05:41.090374+00:00"
DATA_CLASS = "private-local-metadata-and-public-api-contract"
PRIVATE_RECEIPT_ROOT = Path.home() / ".maplab" / "margin-leak-audit"

PRIOR_INVENTORY_RECEIPT = (
    PRIVATE_RECEIPT_ROOT / "20260828-deployed-source-inventory-v1.json"
)
PINNED_PRIOR_RECEIPT_SHA256 = (
    "2110647635fe3223e92bcf5ed421472774b68e339e59c60883f2d683af0dfd21"
)
PINNED_PRIOR_BODY_SHA256 = (
    "c23563deae61f54aee6fa3e9e3b8d0e04b26e473556e2487f1e4dbd13c144fbc"
)

METHOD_CONTRACT = {
    "hypothesis": (
        "a complete static consumer graph, exact local mode snapshot, and "
        "synthetic cutover/readback/rollback gates can produce a safe, "
        "separately reviewable hardening plan without touching live systems"
    ),
    "changed_variable": (
        "replace deployment and root inventory with consumer-complete migration "
        "contracts plus version-bound hash-only Apps Script readback design"
    ),
    "fixed_holdout": (
        "Case Store database and fallback, bot_a6 environment, OpenClaw review "
        "bundles, shared Google credential consumers, quote binding, separate "
        "LINE binding, and header-capable LINE ingress prerequisite"
    ),
    "expected_delta": (
        "every known consumer is pinned; each private surface has an external "
        "owner-only target, atomic cutover/readback/rollback gates; deployed "
        "source remains unresolved until version-bound API readback"
    ),
    "stop_loss": (
        "no chmod, copy, move, restart, deploy, Apps Script API call, credential "
        "use/write, customer row read, source persistence, or private egress"
    ),
    "model": "none",
    "sampling": "fixed-consumer-manifests-and-thirty-nine-policy-gate-fixtures",
    "evaluator": "deterministic-source-mode-scope-cutover-and-receipt-gates",
    "acceptance": (
        "consumer manifests exact, all fixtures meet expected results, current "
        "unsafe modes remain explicit, and live eligibility remains false"
    ),
}

PLATEAU_REVIEW = {
    "prior_method_fingerprints": [
        "a1573a74b88222ae10c2b8edcbeaa9c7bdf2f139596df6be6c33db7b2bea2123",
        "201cf84e8090c12ba743f47f9073dc733a87dd7a57874729b6ce302e4c627133",
        "d282b0fee8655a3cbc075bc332c0eb9ab2e5f18bac05abefdb7d63f97c5f53c0",
    ],
    "same_method_repeated": False,
    "verified_improvement_claimed": False,
    "new_repair_point": "consumer_complete_private_root_and_deployed_readback_plan",
}

PINNED_SOURCE_SHA256 = {
    ".gitignore": "25ccc052e2f738e79fe26cb94f462a7e2977767248bbc5477bcba5baeca8675c",
    "bot/bot.py": "2d185c84edcff85e211a08f914a2b97fb9d29a5bf3d4a1ac6aef81ef3d686814",
    "bot/com.maplab.telegrambot.plist": "ed15bb6352ab215cc2aaed6e0d4f1bee37acf5387a270e63be56e9a25bf8b92a",
    "bot/run_daemon.sh": "177720544aca8d44ef5495fb94703800023c9209a48df216dc9513204bab30dd",
    "bot/test_hermes_fallback.py": "945195cb919c11031eb9e88a90d786fec3a4a84a4d0b2bb21e833aa840feb4c0",
    "bot_a6/.env.example": "12f5f0409c4da73a38623d2c634f66e93d192339fc30b7b33decafc40f1b3391",
    "bot_a6/a2_seo_engine.py": "cd66f6822848c823f53738a9459999bf6a6101d67a8402b73977a7243f246f2c",
    "bot_a6/a5_quote_engine.py": "91b2092713b2c2952fc110171a1e06a2ba33aafd7167ea50d64f6486303668a4",
    "bot_a6/bot_a6.py": "0ad1bba2aa94267427276663695cfabbc8f75e75f06878a8fa46cdeed0cc6774",
    "bot_a6/case_store.py": "5e1e934d3adb1f7d918d72eeef0ef6cc5632d7c52a0d9c52a7138a4772f35007",
    "bot_a6/com.maplab.a6bot.plist": "8d656716087dda4f1605982f1e463e28cab7770b7a3123c33c07b786876aff1a",
    "bot_a6/hermes_deerflow_bridge.py": "fd54d2f749899904b77cb9d97bc05b84bb5c625f2e4fe7287230b989fecb11a2",
    "bot_a6/hermes_task_executor.py": "e6b53c5933d03ee043bf2f34a24ee0d2148efae0d3cc6634082542ab2effe5bf",
    "bot_a6/hermes_telegram_gateway.py": "8388660ecdf2b32564d1afc927fee31a19f27ea15969c427622fc56fb26bdbe5",
    "bot_a6/openclaw_dispatch.py": "dcbb8e1490c1f48c68ff0b4d285c108e5dc3d14c4589c6efc1303a8bcdb9dbc2",
    "bot_a6/run_daemon.sh": "35fc9a95692e54a170b0ed00aa9de0e024699dd1cca2ffc82adc38d77a9c03ba",
    "bot_a6/test_a6_10_rounds.py": "873f1884f8850ec69967cd2befca6b6593c255e820c0adcdd3b68493d8a4060c",
    "chrome-extension/popup.js": "d611773c95decb765d77d3763e5cc6e8b1ad8863a949b53b0f342a35966283b8",
    "chrome-extension/task-modules/A6.json": "0b79f311afaf670f6b06fab7a2b8129c7e2743c48845cf0167ae31f93241914c",
    "config/deerflow/extensions-disabled.json": "439f9f5a1e91d0c3572bc73a2e31e61ac6c91574801453b8d88b6410b38d5d0f",
    "config/deerflow/hermes-public-research-openrouter.yaml": "e7e8a6f28588b7e03c36fc0ddbed000caf1c64261c706f90ffe4617c8fce017d",
    "config/deerflow/hermes-public-research.yaml": "8789be4a2055fa77eaefb0ca6136bdbc43fd4ea89be7abded3224d227d0d5021",
    "config/launchd/com.maplab.hermes-line-training.plist": "32803c238c8e1b8eb06428d7155745c435e537d11da10c88ea77aab4e651793b",
    "docs/openclaw/memory-governance.md": "b56f5e71aa5140134e243c3dfd593fd74e2a3070a33310a37b7665b24310ce69",
    "docs/openclaw/output-contract.md": "368fad433ad22bf1f4fbeef3ef05d4baa179d4f9a93eff8f44639a4d430d03ba",
    "docs/margin-leak-deployed-source-inventory.md": "52e152684375c8b3118302fd7f01d32e6befb676189956b1746bc6dc9c4b43bf",
    "launchd/com.maplab.a6bot.plist": "8d656716087dda4f1605982f1e463e28cab7770b7a3123c33c07b786876aff1a",
    "launchd/com.maplab.hermes-line-training.plist": "32803c238c8e1b8eb06428d7155745c435e537d11da10c88ea77aab4e651793b",
    "launchd/com.maplab.dispatch-backup.plist": "df63ecbd181ceeeb53979b81ef6e0cea01908ad2e681fbea79dc3ba21061317f",
    "launchd/com.maplab.telegrambot.plist": "ed15bb6352ab215cc2aaed6e0d4f1bee37acf5387a270e63be56e9a25bf8b92a",
    "scripts/a6_hermes_activate.sh": "60d6501e3a6219c259f2e3630d5fc744673110902e582ff63d37d3b96345927e",
    "scripts/a4_s11_2024_resume_classifier.py": "14786afe66696a8c7977d2d7703fb786201c60b7f84d2024dfe81999f2bb09b8",
    "scripts/a8_download_drive_case.py": "071af5de34e7c40511d9b9ed5a8ee8cc8be5cb07b1e2a745ba00dbda605e3ec1",
    "scripts/apps-script/.clasp.json": "54d250fd991c659f11b301ae04f73f8e3f0eae2be2d6931392e2f9e99a104bb5",
    "scripts/apps-script/.claspignore": "165d9c88aeaca43de6dccff90eaa0320ccde8de469ce31eb41bd1763c9f715f2",
    "scripts/apps-script/README.md": "0fbccbebeab481a10b75df82bcf9ee6c12cdb0e8426a5fa631dd7d9d115c2cf9",
    "scripts/bot_restart_emergency.sh": "516818c2e7085c9a607b74f7de3d8c28011d1acc1ff7950f4654a4488a61ec8f",
    "scripts/com.maplab.dispatch-backup.plist": "df63ecbd181ceeeb53979b81ef6e0cea01908ad2e681fbea79dc3ba21061317f",
    "scripts/export_a7_line_jsonl.py": "d5ff22d7a168ef4f5d1b93d3831cfe38fad4198a69d74a0da6ed5bc3fc31e39e",
    "scripts/extract_slide_photos_to_items.py": "fb38b017ebc60297b3f8c99ccd17b9ca08dd325f58725ebfa6fd2378921e450c",
    "scripts/health-check.sh": "94364f81955988ea3a510321fcfa9d1f459dd5c90819aeed877aadf22016818d",
    "scripts/hermes_gateway_setup.sh": "6eee6f1ffa5f9f555e8e1b3ce31e972108c57f522715dca9fded2ac51c75ea97",
    "scripts/hermes_line_training_loop.py": "f543777b014ed4a4119b10fd629b9d76d9239d01a601c51e7355fa8a3c521b0d",
    "scripts/hermes_line_schedule_gate_contract.py": "e99db43ec30c8131e49b0b71603103c34141adb5dd408d43e837cf6eedd26d00",
    "scripts/hermes_line_training_supervisor.py": "45fc69de36d1931905e54506577b3074a03e9f38cae23dcb3b4f45bef4ce747d",
    "scripts/local_dispatch_backup.sh": "fa448b6a4ceb4ae4e72b4cd3c3ec79a1ae3c7547268bdda905d0ac03ebf9ef81",
    "scripts/maplab_deployed_source_inventory.py": "447c77a36b7de8c2f86cd8fd243cb468cfadf06d5a0c4893e97e5a9148cd467c",
    "scripts/maplab_margin_google_join_bridge.py": "a26cacb27d4d702235d2e0e2dc4ca895e92177038c28fe7ee56d67f14cefb8a8",
    "scripts/maplab_margin_join_first_shadow.py": "4e229a6ac7f2b499034329f1e587ec79fb3bd1cd36ccfc981670f45537fe88c6",
    "scripts/move_a4_assets_from_sheet.py": "f607678b82cd138b6e8645a391dfd32a1d3097c01539ba7ccca050d64343f9ef",
    "scripts/patrol.sh": "48a9fed15935a2953cd43abdfb23672295dd70cf411214f1eeb642f3c292c075",
    "scripts/sheet_tail.py": "f1e0080790723fe6b8eb8c068e4a1f1f52d212a78d9111bc2d6d536851ade9af",
    "scripts/simulate_a5_quote_requests.py": "37980605df9a83ca8cfd9d51791a65e067fcbce2bf7006b81ebbe0d702f3391e",
    "scripts/update-dashboard.py": "9d3d26cc8fdf00f77bfe716aa4397cac1b0eaeb3f337a79fb1c47c7d1302a902",
    "scripts/update_a6_token.sh": "c321d5e1c9e229f337921417f5771e0f82af4b146ce0bbfeca2c765c775058bf",
    "scripts/weekly_eval_compounding.py": "682236ce25a9e9379dec7bafb85af6aa3fce3fb2ff770f782133a3050584f2d1",
    "scripts/搜尋_缺圖品項_WordPress_pipeline.py": "adbaf77092ba4829380c1859b1553c5af4815aca4d05e5036aab6b06c6b410f9",
    "scripts/整理_品項圖片_pipeline.py": "abeb674b64cda5530e78eed58c6b972b17ae6f459e6d32874ac1a692499886c6",
    "scripts/相似品項共用_第二輪.py": "6736a0aae610ce4404a7a3cc8a8c913fd1e432b850f09b5091761967b3444b65",
    "tools/ai_workbook/a8_spec_card_generator.py": "b260da7df782729baf4670f9f27745ac0bdb63e5b0976673c43357e34a77dddd",
    "tools/ai_workbook/asset_case_matcher.py": "08341fb8520bf9b967c9c1ad2289093b386dbaa5cd8cededf2860fdebf4e3da4",
    "tools/ai_workbook/build_extension_task_modules.py": "286ad7581dba9c055721c39f76af0bc99e705c8510ee2ae4f166ad35144884f9",
    "tools/ai_workbook/openclaw_adapter.py": "e02ccbd0db33fa277640924171f81c5bb336afe715acf1f48cc46f5de0808aa4",
    "tools/ai_workbook/paths.py": "ed2663e28fe3530f5c5151d30173dd942254b001d0b4443c4b3d4952314b9a2a",
    "tools/ai_workbook/photo_pipeline.py": "3e526f64b66fc2bda3c0670e36d4c15775f53578c71542e965857f4e20730c5b",
    "tools/google_reindex_submit.py": "74974b205e71a4f7df36247e9fa22c830c01855219855d79dbac89065b760d0a",
    "tools/wp_rankmath_recovery.py": "a634bb9aa5e1b1c21573015de58c2aa53788ac2b9bc62be58b0c4755f19e1636",
    "workbook/reviews/README.md": "91c65b9321e7f66e9ae0299d9f6832c3e01c8e8e6ef1c54daa3bc7f358691add",
    "workbook/system_index/system_relation_index.csv": "794eab190f45499484de899add9f9ec2ca58baff1fa6474b4181c47d7bc3a79b",
}


@dataclass(frozen=True)
class Consumer:
    surface: str
    path: str
    role: str
    anchors: tuple[str, ...]


CONSUMERS = (
    Consumer("case_store", "bot_a6/bot_a6.py", "runtime_sync", ("CaseStore.from_env(REPO_PATH)",)),
    Consumer("case_store", "bot_a6/case_store.py", "db_and_fallback_resolver", ("CASE_STORE_DB_PATH", "CASE_STORE_FALLBACK_JSON")),
    Consumer("case_store", "scripts/export_a7_line_jsonl.py", "direct_db_exporter", ("a6_case_store.sqlite3",)),
    Consumer("case_store", "scripts/maplab_deployed_source_inventory.py", "inventory_reader", ("a6_case_store.sqlite3", "CASE_STORE_FALLBACK_JSON")),
    Consumer("case_store", "bot_a6/.env.example", "configuration_template", ("CASE_STORE_DB_PATH", "CASE_STORE_FALLBACK_JSON")),
    Consumer("case_store", "scripts/local_dispatch_backup.sh", "daily_copy_and_index", ("rsync -a --delete", "maplab_backup")),
    Consumer("bot_env", "bot_a6/run_daemon.sh", "runtime_loader", ('source "$BOT_DIR/.env"',)),
    Consumer("bot_env", "bot_a6/bot_a6.py", "python_loader", ('load_dotenv(BOT_DIR / ".env")',)),
    Consumer("bot_env", "launchd/com.maplab.a6bot.plist", "service_entrypoint", ("bot_a6/run_daemon.sh",)),
    Consumer("bot_env", "bot_a6/com.maplab.a6bot.plist", "duplicate_service_definition", ("com.maplab.a6bot",)),
    Consumer("bot_env", "bot_a6/hermes_telegram_gateway.py", "active_inherited_env_consumer", ("A6_BOT_TOKEN", "OWNER_USER_ID")),
    Consumer("bot_env", "bot_a6/hermes_task_executor.py", "active_inherited_env_policy_consumer", ('os.environ.get("HERMES_DEERFLOW_PROVIDER"', 'os.environ.get("HERMES_DEERFLOW_OPENROUTER_POLICY_VERIFIED"', 'os.environ.get("HERMES_DEERFLOW_ALLOW_PAID"', 'os.environ.get("HERMES_LINE_DATA_ROOT"')),
    Consumer("bot_env", "bot_a6/hermes_deerflow_bridge.py", "active_inherited_env_provider_consumer", ('os.environ.get("HERMES_DEERFLOW_OPENROUTER_POLICY_VERIFIED"', 'os.environ.get("HERMES_DEERFLOW_ALLOW_PAID"', 'os.environ.get("OPENROUTER_API_KEY"')),
    Consumer("bot_env", "scripts/update_a6_token.sh", "credential_writer_and_restart", ("bot_a6/.env", "launchctl kickstart")),
    Consumer("bot_env", "scripts/health-check.sh", "legacy_path_health_check", ("bot_a6/.env",)),
    Consumer("bot_env", "scripts/maplab_deployed_source_inventory.py", "environment_inventory_reader", ('env_keys = _env_key_names(root / "bot_a6" / ".env")', 'repo_path_value = _env_value(root / "bot_a6" / ".env", "REPO_PATH")')),
    Consumer("bot_env", "scripts/a6_hermes_activate.sh", "runtime_switcher", ("com.maplab.a6bot.plist",)),
    Consumer("bot_env", "scripts/bot_restart_emergency.sh", "runtime_restart_switcher", ("com.maplab.a6bot",)),
    Consumer("bot_env", "scripts/local_dispatch_backup.sh", "daily_secret_copy", ("rsync -a --delete",)),
    Consumer("provider_credential", "bot_a6/hermes_telegram_gateway.py", "active_free_compute_secret_reader", ("FREE_ENV = Path.home()", "def load_free_env_key()", "FREE_ENV.read_text")),
    Consumer("provider_credential", "scripts/hermes_gateway_setup.sh", "free_compute_to_hermes_secret_copy_writer", ('FREE_ENV="$HOME/.maplab/free_compute.env"', 'ENV_FILE="$HERMES_HOME/.env"', 'grep "^OPENROUTER_API_KEY=" "$FREE_ENV" >> "$ENV_FILE"')),
    Consumer("provider_credential", "bot_a6/hermes_task_executor.py", "inherited_openrouter_secret_projector", ('"OPENROUTER_API_KEY": openrouter_key',)),
    Consumer("provider_credential", "bot_a6/hermes_deerflow_bridge.py", "inherited_openrouter_secret_consumer", ('os.environ.get("OPENROUTER_API_KEY")',)),
    Consumer("provider_credential", "config/deerflow/hermes-public-research-openrouter.yaml", "openrouter_key_placeholder_and_policy_config", ("api_key: $OPENROUTER_API_KEY", "base_url: https://openrouter.ai/api/v1", "zdr: true", "data_collection: deny")),
    Consumer("provider_runtime_config", "config/deerflow/hermes-public-research.yaml", "local_provider_fail_closed_config", ("model: gemma4:latest", "base_url: http://127.0.0.1:11434", "tool_groups: []", "tools: []")),
    Consumer("provider_runtime_config", "config/deerflow/extensions-disabled.json", "disabled_extension_registry", ('"mcpServers": {}', '"skills": {}', '"plugins": []')),
    Consumer("hermes_line_training", "bot_a6/com.maplab.a6bot.plist", "service_training_root_binding", ("HERMES_LINE_DATA_ROOT", "a6-hermes-training")),
    Consumer("hermes_line_training", "launchd/com.maplab.a6bot.plist", "duplicate_service_training_root_binding", ("HERMES_LINE_DATA_ROOT", "a6-hermes-training")),
    Consumer("hermes_line_training", "bot_a6/hermes_task_executor.py", "training_root_inherited_consumer", ('os.environ.get("HERMES_LINE_DATA_ROOT")',)),
    Consumer("hermes_line_training", "config/launchd/com.maplab.hermes-line-training.plist", "scheduled_training_root_binding", ("HERMES_LINE_DATA_ROOT", "hermes_line_training_supervisor.py", "--job-path")),
    Consumer("hermes_line_training", "launchd/com.maplab.hermes-line-training.plist", "duplicate_scheduled_training_root_binding", ("HERMES_LINE_DATA_ROOT", "hermes_line_training_supervisor.py", "--job-path")),
    Consumer("hermes_line_training", "scripts/hermes_line_training_loop.py", "training_root_resolver", ('os.environ.get("HERMES_LINE_DATA_ROOT")', "DEFAULT_DATA_ROOT")),
    Consumer("hermes_line_training", "scripts/hermes_line_schedule_gate_contract.py", "scheduled_route_contract_validator", ("HERMES_LINE_DATA_ROOT", "EXPECTED_ARGUMENTS", "raw_loop_side_door")),
    Consumer("hermes_line_training", "scripts/hermes_line_training_supervisor.py", "training_root_child_env_projector", ('"HERMES_LINE_DATA_ROOT": str(data_root)',)),
    Consumer("openclaw_review", "tools/ai_workbook/paths.py", "review_root_definition", ("REVIEWS_DIR = WORKBOOK_DIR / \"reviews\"",)),
    Consumer("openclaw_review", "tools/ai_workbook/openclaw_adapter.py", "bundle_writer", ("from .paths import REVIEWS_DIR", "bundle_dir = REVIEWS_DIR / job_id")),
    Consumer("openclaw_review", "bot_a6/a2_seo_engine.py", "adapter_caller_and_reader", ("OpenClawAdapter(default_model=requested_model)", "draft_md")),
    Consumer("openclaw_review", "bot_a6/a5_quote_engine.py", "adapter_caller_and_postseal_mutator", ("OpenClawAdapter(default_model=requested_model)", "draft_md")),
    Consumer("openclaw_review", "bot_a6/openclaw_dispatch.py", "adapter_caller_and_postseal_writer", ("self.adapter = OpenClawAdapter", "routing.json")),
    Consumer("openclaw_review", "scripts/simulate_a5_quote_requests.py", "bundle_path_reporter", ("bundle_dir",)),
    Consumer("openclaw_review", "bot_a6/test_a6_10_rounds.py", "live_adapter_test_caller", ("run_a5_local_quote",)),
    Consumer("openclaw_review", "scripts/weekly_eval_compounding.py", "draft_discovery_reader", ("workbook/reviews/",)),
    Consumer("openclaw_review", "tools/ai_workbook/build_extension_task_modules.py", "contract_generator", ("default_review_bundle", "workbook/reviews/JOB-xxx/")),
    Consumer("openclaw_review", "chrome-extension/popup.js", "generated_prompt_consumer", ("default_review_bundle",)),
    Consumer("openclaw_review", "chrome-extension/task-modules/A6.json", "materialized_contract_consumer", ("default_review_bundle",)),
    Consumer("openclaw_review", "workbook/system_index/system_relation_index.csv", "discovery_index_consumer", ("workbook/reviews/JOB-*/",)),
    Consumer("openclaw_review", "workbook/reviews/README.md", "human_review_contract", ("Codex writes the bundle",)),
    Consumer("openclaw_review", "docs/openclaw/memory-governance.md", "human_memory_contract", ("workbook/reviews/JOB-xxx/",)),
    Consumer("openclaw_review", "docs/openclaw/output-contract.md", "human_output_contract", ("workbook/reviews/JOB-xxx/",)),
    Consumer("shared_review_non_adapter", "tools/wp_rankmath_recovery.py", "classified_fixed_artifact_writer", ("job_dir = REVIEWS_DIR / args.job", 'write_json(job_dir / "execution_log.json"', 'write_json(job_dir / "output_manifest.json"', '(job_dir / "review_request.md").write_text')),
    Consumer("shared_review_non_adapter", "tools/google_reindex_submit.py", "classified_fixed_artifact_writer", ("job_dir = REVIEWS_DIR / args.job", 'write_json(job_dir / "execution_log.json"', 'write_json(job_dir / "output_manifest.json"', '(job_dir / "review_request.md").write_text')),
    Consumer("openclaw_dispatch", "bot/bot.py", "live_dispatch_writer_reader", ("MAPLAB_DISPATCH_DIR", "telegram-dispatch")),
    Consumer("openclaw_dispatch", "bot/run_daemon.sh", "live_launcher_without_umask", ("bot.py",)),
    Consumer("openclaw_dispatch", "bot/com.maplab.telegrambot.plist", "live_service_definition", ("com.maplab.telegrambot",)),
    Consumer("openclaw_dispatch", "launchd/com.maplab.telegrambot.plist", "duplicate_service_definition", ("com.maplab.telegrambot",)),
    Consumer("openclaw_dispatch", "bot/test_hermes_fallback.py", "dispatch_contract_test", ("_write_dispatch_packet", "DISPATCH_DIR")),
    Consumer("openclaw_dispatch", "bot/bot.py", "temporary_clipboard_writer_server", ('CLIP_FILE = Path("/tmp/maplab_clip.json")', 'self.path != "/clip"')),
    Consumer("openclaw_dispatch", "chrome-extension/popup.js", "temporary_clipboard_reader", ("127.0.0.1:9876/clip",)),
    Consumer("backup", "scripts/local_dispatch_backup.sh", "private_copy_propagator", ("BACKUP_BASE", "rsync -a --delete")),
    Consumer("backup", "launchd/com.maplab.dispatch-backup.plist", "scheduled_backup_entrypoint", ("local_dispatch_backup.sh",)),
    Consumer("backup", "scripts/com.maplab.dispatch-backup.plist", "duplicate_backup_definition", ("local_dispatch_backup.sh",)),
    Consumer("gas_binding", "scripts/apps-script/.clasp.json", "quote_local_binding", ("scriptId",)),
    Consumer("gas_binding", "scripts/apps-script/.claspignore", "quote_source_selection", ("LineWebhook.gs",)),
    Consumer("gas_binding", "scripts/apps-script/README.md", "separate_line_checkout_declaration", ("scripts/apps-script-line/",)),
)


GOOGLE_TOKEN_CONSUMERS = {
    "bot_a6/.env.example": "configuration_template",
    "bot_a6/case_store.py": "read_with_env_override",
    "scripts/a4_s11_2024_resume_classifier.py": "read_and_refresh_write",
    "scripts/a8_download_drive_case.py": "read",
    "scripts/extract_slide_photos_to_items.py": "read_and_refresh_write",
    "scripts/maplab_deployed_source_inventory.py": "metadata_only",
    "scripts/maplab_margin_google_join_bridge.py": "read_with_cli_override",
    "scripts/maplab_margin_join_first_shadow.py": "read_with_cli_override",
    "scripts/move_a4_assets_from_sheet.py": "read_and_refresh_write",
    "scripts/patrol.sh": "read_and_refresh_write",
    "scripts/sheet_tail.py": "read_with_cli_override",
    "scripts/update-dashboard.py": "read_and_refresh_write",
    "scripts/搜尋_缺圖品項_WordPress_pipeline.py": "read_and_refresh_write",
    "scripts/整理_品項圖片_pipeline.py": "read_and_refresh_write",
    "scripts/相似品項共用_第二輪.py": "read_and_refresh_write",
    "tools/ai_workbook/a8_spec_card_generator.py": "read",
    "tools/ai_workbook/asset_case_matcher.py": "read_and_refresh_write",
    "tools/ai_workbook/photo_pipeline.py": "read",
    "tools/google_reindex_submit.py": "metadata_and_read",
}

PRIVATE_ENV_REFERENCE_CONSUMERS = {
    "bot_a6/com.maplab.a6bot.plist": "a6_training_root_binding",
    "bot_a6/hermes_deerflow_bridge.py": "inherited_openrouter_key_consumer",
    "bot_a6/hermes_task_executor.py": "provider_policy_and_training_root_consumer",
    "bot_a6/hermes_telegram_gateway.py": "free_compute_env_direct_reader",
    "config/deerflow/hermes-public-research-openrouter.yaml": "openrouter_key_placeholder_and_policy_config",
    "config/launchd/com.maplab.hermes-line-training.plist": "scheduled_training_root_binding",
    "launchd/com.maplab.hermes-line-training.plist": "duplicate_scheduled_training_root_binding",
    "launchd/com.maplab.a6bot.plist": "duplicate_a6_training_root_binding",
    "scripts/hermes_gateway_setup.sh": "free_compute_to_hermes_env_writer",
    "scripts/hermes_line_training_loop.py": "training_root_resolver",
    "scripts/hermes_line_schedule_gate_contract.py": "scheduled_route_contract_validator",
    "scripts/hermes_line_training_supervisor.py": "training_root_child_env_projector",
}

EXTERNAL_GOOGLE_TOKEN_CONSUMERS = {
    "drive_smoke": {
        "home_relative_path": ".claude/mcp-keys/drive_smoke_upload.py",
        "role": "read_and_upload_smoke",
        "sha256": "754575667811d4efe17ba448ea06c7e1431e8da0183097f7a5d73297707fc2a1",
        "expected_mode": 0o644,
        "required_anchor": "google-token.json",
        "payload_class": "source_code",
    },
    "gsc_pull": {
        "home_relative_path": ".claude/mcp-keys/gsc_pull.py",
        "role": "read_and_webmasters_query",
        "sha256": "938c4e38616cd388e768c7b88210c6c027b09e9b1a6a10a6556182cd99a02db3",
        "expected_mode": 0o644,
        "required_anchor": "google-token.json",
        "payload_class": "source_code",
    },
    "reauth": {
        "home_relative_path": ".claude/mcp-keys/reauth_google.py",
        "role": "interactive_refresh_writer",
        "sha256": "aa43611867f4e43d82032cad3064279cec25c755f37127c398e35520a6f48e91",
        "expected_mode": 0o644,
        "required_anchor": "google-token.json",
        "payload_class": "source_code",
    },
    "mcp_config": {
        "home_relative_path": ".claude/.mcp.json",
        "role": "unversioned_mcp_runtime_consumer",
        "sha256": "d7524de3ef6dcef1c19bd56b2c13f07cf7f7a918108a9f61b6cec189f28da3c3",
        "expected_mode": 0o644,
        "required_anchor": "mcp-google-sheets@latest",
        "payload_class": "secret_config",
    },
}

OPENCLAW_BUNDLE_FILENAMES = {
    "task_request.md",
    "output.json",
    "draft.md",
    "execution_log.json",
    "verification_log.json",
    "review_request.md",
    "output_manifest.json",
    "terminal.log",
    "routing.json",
}

ADAPTER_SIGNATURE_PATHS = (
    "task_request.md",
    "output.json",
    "draft.md",
    "execution_log.json",
    "verification_log.json",
    "review_request.md",
    "output_manifest.json",
    "screenshots/terminal.log",
)

LEGACY_MANIFEST_PATHS = {
    "task_request.md",
    "output.json",
    "draft.md",
    "execution_log.json",
    "verification_log.json",
    "review_request.md",
}

EXTERNAL_RUNTIME_CONSUMERS = {
    "a6_launchagent": {
        "home_relative_path": "Library/LaunchAgents/com.maplab.a6bot.plist",
        "role": "installed_a6_service_definition",
        "sha256": "8d656716087dda4f1605982f1e463e28cab7770b7a3123c33c07b786876aff1a",
        "expected_mode": 0o644,
    },
    "backup_launchagent": {
        "home_relative_path": "Library/LaunchAgents/com.maplab.dispatch-backup.plist",
        "role": "installed_backup_service_definition",
        "sha256": "df63ecbd181ceeeb53979b81ef6e0cea01908ad2e681fbea79dc3ba21061317f",
        "expected_mode": 0o644,
    },
    "hermes_line_training_launchagent": {
        "home_relative_path": "Library/LaunchAgents/com.maplab.hermes-line-training.plist",
        "role": "installed_hermes_line_training_definition",
        "sha256": "32803c238c8e1b8eb06428d7155745c435e537d11da10c88ea77aab4e651793b",
        "expected_mode": 0o644,
    },
    "telegram_launchagent": {
        "home_relative_path": "Library/LaunchAgents/com.maplab.telegrambot.plist",
        "role": "installed_telegram_dispatch_service_definition",
        "sha256": "ed15bb6352ab215cc2aaed6e0d4f1bee37acf5387a270e63be56e9a25bf8b92a",
        "expected_mode": 0o644,
    },
}

APPS_SCRIPT_READONLY_SCOPES = (
    "https://www.googleapis.com/auth/script.deployments.readonly",
    "https://www.googleapis.com/auth/script.projects.readonly",
)

TARGET_CONTRACTS = {
    "case_store": {
        "root_symbol": "MAPLAB_PRIVATE_CASE_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "env-path-cas-then-supervised-restart",
        "readback": "sqlite-backup-integrity-row-count-and-fallback-json-digest",
        "rollback": "pre-write-may-restore-old-config;post-write-keeps-external-authority-and-forward-repairs-never-repo",
    },
    "bot_env": {
        "root_symbol": "MAPLAB_PRIVATE_BOT_CONFIG_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "launchd-env-file-path-cas-then-supervised-restart",
        "readback": "key-name-set-and-redacted-value-fingerprint-plus-service-health",
        "rollback": "switch-to-prior-sealed-external-generation-never-repo-env",
    },
    "provider_credential": {
        "root_symbol": "MAPLAB_PRIVATE_PROVIDER_CONFIG_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "single-sealed-authority-with-consumer-scoped-projections-and-no-setup-copy-writer",
        "readback": "reader-writer-manifest-key-name-set-redacted-fingerprint-and-zero-duplicate-authorities",
        "rollback": "switch-prior-sealed-generation-before-refresh;after-refresh-forward-repair-never-unsafe-source-parent",
    },
    "hermes_line_training": {
        "root_symbol": "HERMES_LINE_DATA_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "retain-owner-only-root-and-cas-all-source-plus-installed-runtime-bindings",
        "readback": "root-directory-and-file-mode-histograms-plus-loop-supervisor-and-launchagent-binding",
        "rollback": "switch-runtime-binding-to-prior-sealed-owner-only-generation-never-repo-or-cloud",
    },
    "openclaw_review": {
        "root_symbol": "MAPLAB_PRIVATE_OPENCLAW_REVIEW_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "signature-scoped-logical-locator-cas-after-copy-and-actual-byte-ledger",
        "readback": "forty-four-adapter-bundles-actual-byte-ledger-sealed-after-terminal-and-routing",
        "rollback": "switch-locator-generation-only-never-write-back-to-repo",
    },
    "shared_review_non_adapter": {
        "root_symbol": "MAPLAB_PRIVATE_SHARED_REVIEW_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "classified-fixed-artifact-logical-locator-cas-after-copy-and-actual-byte-ledger",
        "readback": "fifty-three-current-non-adapter-fixed-artifacts-plus-future-classified-writes-external-only",
        "rollback": "switch-classified-artifact-locator-generation-only-never-write-private-bytes-back-to-shared-repo",
    },
    "openclaw_dispatch": {
        "root_symbol": "MAPLAB_PRIVATE_OPENCLAW_DISPATCH_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "separate-dispatch-root-cas-with-new-writes-external-only",
        "readback": "packet-count-hash-mode-no-physical-path-and-no-temp-clipboard",
        "rollback": "switch-dispatch-locator-generation-or-fail-closed-never-repo-fallback",
    },
    "extension_clipboard": {
        "root_symbol": "MAPLAB_PRIVATE_CLIPBOARD_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "replace-system-temp-file-with-single-use-loopback-broker-or-owner-only-generation",
        "readback": "single-use-expiry-owner-only-mode-and-zero-system-temp-copy",
        "rollback": "disable-feature-fail-closed-never-system-temp-fallback",
    },
    "backup_policy": {
        "root_symbol": "MAPLAB_PRIVATE_BACKUP_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "exclude-private-repo-paths-before-any-source-retirement",
        "readback": "next-backup-index-zero-sensitive-paths-and-owner-only-private-snapshot",
        "rollback": "restore-backup-code-only-never-reintroduce-private-repo-copying",
    },
    "shared_google_credential": {
        "root_symbol": "MAPLAB_PRIVATE_GOOGLE_CONFIG_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "patch-all-current-manifested-consumers-then-atomic-path-cas",
        "readback": "consumer-manifest-key-set-scope-set-and-no-secret-output",
        "rollback": "pre-refresh-may-switch-prior-sealed-external-generation;post-refresh-keeps-external-authority-and-forward-repairs-never-unsafe-old-token",
    },
    "apps_script_readback_credential": {
        "root_symbol": "MAPLAB_APPS_SCRIPT_READONLY_CONFIG_ROOT",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "separate-dedicated-credential-never-shared-token-scope-expansion",
        "readback": "exact-two-readonly-scopes-and-zero-write-methods",
        "rollback": "disable-dedicated-readback-profile-with-shared-token-unchanged",
    },
    "clasp_credential": {
        "root_symbol": "CLASP_CREDENTIAL_OUT_OF_READBACK_SCOPE",
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "directory_mode": 0o700,
        "file_mode": 0o600,
        "symlink_allowed": False,
        "cutover": "never-use-clasp-credential-for-hash-only-readback",
        "readback": "metadata-only-mode-gate",
        "rollback": "no-change-because-profile-is-not-used",
    },
}

TARGET_OWNERSHIP_CONTRACT = {
    "owner_uid": "effective-user",
    "parent_chain_owner_uid_required": True,
    "regular_files_only": True,
    "hardlink_allowed": False,
    "acl_entries_allowed": False,
}
for _target_contract in TARGET_CONTRACTS.values():
    _target_contract.update(TARGET_OWNERSHIP_CONTRACT)

READBACK_PLAN = {
    "status": "DESIGNED_NOT_EXECUTED",
    "credential_profile": "DEDICATED_APPS_SCRIPT_READONLY",
    "reuse_shared_google_credential": False,
    "required_scopes": list(APPS_SCRIPT_READONLY_SCOPES),
    "deployment_lookup_method": "projects.deployments.get",
    "versioned_content_method": "projects.getContent(versionNumber)",
    "head_only_is_deployed_truth": False,
    "version_number_must_equal_deployment_config": True,
    "deployment_metadata_double_read_required": True,
    "deployment_version_and_update_time_must_remain_stable": True,
    "canonicalization": "api-canonical-tree-v1-sort-type-name-hash-name-type-exact-source",
    "raw_source_persisted": False,
    "raw_identifiers_persisted": False,
    "identifier_receipt_form": "salted-sha256-only",
    "per_target_planned_read_calls": 3,
    "write_methods_allowed": [],
    "transport_methods_allowed": ["GET"],
    "transport_get_only": True,
    "clasp_allowed": False,
    "shared_mcp_allowed": False,
    "api_enabled_resolved": False,
    "principal_access_resolved": False,
    "quote_current_deployed_truth_resolved": False,
    "line_current_deployed_truth_resolved": False,
    "line_current_binding_verified": False,
    "direct_gas_line_signature_authority": False,
    "header_capable_line_ingress_phase": 0,
}


class HardeningPlanError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(f"{code}: {detail}" if detail else code)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def method_fingerprint() -> str:
    return _sha256_bytes(
        _canonical_json(
            {
                "method_version": METHOD_VERSION,
                "method_contract": METHOD_CONTRACT,
                "plateau_review": PLATEAU_REVIEW,
                "source_manifest": PINNED_SOURCE_SHA256,
                "consumer_manifest": [
                    [item.surface, item.path, item.role, list(item.anchors)]
                    for item in CONSUMERS
                ],
                "google_consumer_manifest": GOOGLE_TOKEN_CONSUMERS,
                "private_env_reference_manifest": PRIVATE_ENV_REFERENCE_CONSUMERS,
                "external_google_consumer_manifest": EXTERNAL_GOOGLE_TOKEN_CONSUMERS,
                "external_runtime_consumer_manifest": EXTERNAL_RUNTIME_CONSUMERS,
                "target_contracts": TARGET_CONTRACTS,
                "readback_plan": READBACK_PLAN,
            }
        )
    )


def _mode(path: Path) -> int | None:
    try:
        return stat.S_IMODE(path.lstat().st_mode)
    except FileNotFoundError:
        return None


def _has_symlink_component(path: Path) -> bool:
    current = path
    while True:
        if current.is_symlink():
            return True
        if current.parent == current:
            return False
        current = current.parent


def _is_regular_no_symlink(path: Path) -> bool:
    return path.exists() and path.is_file() and not _has_symlink_component(path)


def inspect_source_pins(
    repo_root: Path, overrides: dict[str, bytes] | None = None
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    overrides = overrides or {}
    for relative, expected in sorted(PINNED_SOURCE_SHA256.items()):
        path = repo_root / relative
        trusted = _is_regular_no_symlink(path)
        actual = (
            _sha256_bytes(overrides[relative])
            if relative in overrides
            else _sha256_file(path)
            if trusted
            else None
        )
        matches = trusted and actual == expected
        rows.append(
            {
                "path": relative,
                "sha256": actual,
                "matches_pinned": matches,
                "status": "MATCH" if matches else "DRIFT_OR_MISSING",
            }
        )
    return rows


def inspect_consumers(repo_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in CONSUMERS:
        path = repo_root / item.path
        trusted = _is_regular_no_symlink(path)
        text = path.read_text(encoding="utf-8") if trusted else ""
        anchors_present = trusted and all(anchor in text for anchor in item.anchors)
        rows.append(
            {
                "surface": item.surface,
                "path": item.path,
                "role": item.role,
                "anchor_count": len(item.anchors),
                "anchors_present": anchors_present,
                "status": "MATCH" if anchors_present else "DRIFT_OR_MISSING",
            }
        )
    return rows


def scan_google_token_references(repo_root: Path) -> set[str]:
    token_name = "google-" + "token.json"
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "grep",
            "-l",
            "-F",
            "-z",
            "-e",
            token_name,
            "-e",
            "--google-token",
            "--",
            "bot_a6",
            "scripts",
            "tools",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise HardeningPlanError("GOOGLE_CONSUMER_GIT_QUERY")
    return {
        value.decode("utf-8")
        for value in result.stdout.split(b"\0")
        if value
        and value.decode("utf-8")
        != "scripts/maplab_private_root_hardening_plan.py"
    }


def scan_private_env_references(repo_root: Path) -> set[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "grep",
            "-l",
            "-z",
            "-E",
            "-e",
            r"free_compute\.env|OPENROUTER_API_KEY|HERMES_LINE_DATA_ROOT",
            "--",
            "bot_a6/*.py",
            "bot_a6/*.sh",
            "bot_a6/*.plist",
            "scripts/*.py",
            "scripts/*.sh",
            "config/deerflow/*.yaml",
            "config/launchd/*.plist",
            "launchd/*.plist",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise HardeningPlanError("PRIVATE_ENV_REFERENCE_GIT_QUERY")
    return {
        value.decode("utf-8")
        for value in result.stdout.split(b"\0")
        if value
        and value.decode("utf-8")
        != "scripts/maplab_private_root_hardening_plan.py"
    }


def inspect_private_env_reference_consumers(repo_root: Path) -> dict[str, Any]:
    found = scan_private_env_references(repo_root)
    expected = set(PRIVATE_ENV_REFERENCE_CONSUMERS)
    return {
        "repo_reference_count": len(found),
        "repo_scan_scope": "git-index-tracked-active-python-shell-and-launchd",
        "repo_manifest": [
            {"path": path, "role": PRIVATE_ENV_REFERENCE_CONSUMERS[path]}
            for path in sorted(expected)
        ],
        "repo_missing": sorted(expected - found),
        "repo_unexpected": sorted(found - expected),
        "repo_manifest_complete": found == expected,
        "repo_consumers_all_source_pinned": expected <= set(PINNED_SOURCE_SHA256),
        "private_payload_reads": 0,
    }


def inspect_google_consumers(repo_root: Path) -> dict[str, Any]:
    found = scan_google_token_references(repo_root)
    expected = set(GOOGLE_TOKEN_CONSUMERS)
    external_rows: list[dict[str, Any]] = []
    safe_source_verified_count = 0
    secret_config_metadata_only_count = 0
    for alias, contract in sorted(EXTERNAL_GOOGLE_TOKEN_CONSUMERS.items()):
        path = Path.home() / contract["home_relative_path"]
        trusted = _is_regular_no_symlink(path)
        metadata_matches = trusted and _mode(path) == contract["expected_mode"]
        safe_source = contract["payload_class"] == "source_code"
        current_sha = _sha256_file(path) if trusted and safe_source else None
        matches_pinned: bool | None = (
            current_sha == contract["sha256"] if safe_source else None
        )
        if safe_source and metadata_matches and matches_pinned is True:
            safe_source_verified_count += 1
        if not safe_source and metadata_matches:
            secret_config_metadata_only_count += 1
        external_rows.append(
            {
                "alias": alias,
                "role": contract["role"],
                "payload_class": contract["payload_class"],
                "prior_sha256": contract["sha256"],
                "current_sha256": current_sha,
                "file_mode": _mode(path),
                "file_present": trusted,
                "current_read_mode": "HASH_ONLY_SOURCE_CODE" if safe_source else "NONE",
                "prior_anchor_bound_by_digest": True,
                "metadata_matches": metadata_matches,
                "matches_pinned": matches_pinned,
                "status": (
                    "MATCH"
                    if safe_source and metadata_matches and matches_pinned is True
                    else "PRIOR_PIN_MODE_MATCH_SECRET_CONFIG_UNREAD"
                    if not safe_source and metadata_matches
                    else "DRIFT_OR_MISSING"
                ),
            }
        )
    return {
        "repo_reference_count": len(found),
        "repo_scan_scope": "git-index-tracked-bot_a6-scripts-tools",
        "external_reference_count": len(external_rows),
        "total_known_consumer_count": len(found) + len(external_rows),
        "repo_manifest": [
            {"path": path, "role": GOOGLE_TOKEN_CONSUMERS[path]}
            for path in sorted(expected)
        ],
        "external_manifest": external_rows,
        "repo_missing": sorted(expected - found),
        "repo_unexpected": sorted(found - expected),
        "repo_manifest_complete": found == expected,
        "repo_consumers_all_source_pinned": expected <= set(PINNED_SOURCE_SHA256),
        "safe_external_source_count": 3,
        "safe_external_source_verified_count": safe_source_verified_count,
        "secret_config_metadata_only_count": secret_config_metadata_only_count,
        "external_payload_current_verified": False,
        "live_cutover_consumer_truth_complete": False,
    }


def inspect_external_runtime_consumers() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for alias, contract in sorted(EXTERNAL_RUNTIME_CONSUMERS.items()):
        path = Path.home() / contract["home_relative_path"]
        trusted = _is_regular_no_symlink(path)
        actual_sha = _sha256_file(path) if trusted else None
        matches = (
            trusted
            and actual_sha == contract["sha256"]
            and _mode(path) == contract["expected_mode"]
        )
        rows.append(
            {
                "alias": alias,
                "role": contract["role"],
                "sha256": actual_sha,
                "file_mode": _mode(path),
                "matches_pinned": matches,
                "runtime_binding_readback": False,
                "status": (
                    "INSTALLED_FILE_MATCH_RUNTIME_BINDING_UNRESOLVED"
                    if matches
                    else "DRIFT_OR_MISSING"
                ),
            }
        )
    return rows


def _git_tracked_paths(repo_root: Path, path: Path) -> set[str]:
    process = subprocess.run(
        ["git", "ls-files", "-z", "--", path.relative_to(repo_root).as_posix()],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    return {
        value
        for value in process.stdout.decode("utf-8", errors="strict").split("\0")
        if value
    }


def _mode_histogram(paths: Iterable[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in paths:
        mode = _mode(path)
        key = f"{mode:04o}" if mode is not None else "missing"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _inspect_openclaw_review(repo_root: Path) -> dict[str, Any]:
    review_root = repo_root / "workbook" / "reviews"
    manifest_metadata_reads = 0
    review_request_text_reads = 0
    generic_files = [
        path
        for path in review_root.rglob("*")
        if path.name in OPENCLAW_BUNDLE_FILENAMES
        and path.is_file()
        and not path.is_symlink()
    ]
    generic_symlinks = sum(
        1
        for path in review_root.rglob("*")
        if path.name in OPENCLAW_BUNDLE_FILENAMES and path.is_symlink()
    )
    bundle_dirs = sorted(
        path.parent
        for path in review_root.rglob("output_manifest.json")
        if _is_regular_no_symlink(path)
        and all(_is_regular_no_symlink(path.parent / item) for item in ADAPTER_SIGNATURE_PATHS)
    )

    adapter_files: list[Path] = []
    manifest_mismatch_count = 0
    terminal_unsealed_count = 0
    routing_unsealed_count = 0
    embedded_absolute_bundle_count = 0
    embedded_absolute_review_count = 0
    private_hash_reads = 0
    hardlink_count = 0
    bundle_symlink_component_count = 0
    for bundle in bundle_dirs:
        expected_paths = [bundle / relative for relative in ADAPTER_SIGNATURE_PATHS]
        adapter_files.extend(
            path for path in expected_paths if _is_regular_no_symlink(path)
        )
        if _has_symlink_component(bundle):
            bundle_symlink_component_count += 1
        hardlink_count += sum(
            1 for path in expected_paths if _is_regular_no_symlink(path) and path.stat().st_nlink > 1
        )
        manifest_path = bundle / "output_manifest.json"
        manifest_metadata_reads += 1
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            manifest_mismatch_count += len(LEGACY_MANIFEST_PATHS) + 1
            continue
        if Path(str(manifest.get("bundle_dir", ""))).is_absolute():
            embedded_absolute_bundle_count += 1
        listed_paths: set[str] = set()
        for row in manifest.get("files", []):
            if not isinstance(row, dict):
                manifest_mismatch_count += 1
                continue
            raw_value = str(row.get("path", ""))
            raw_path = Path(raw_value)
            if (
                raw_value not in LEGACY_MANIFEST_PATHS
                or raw_path.is_absolute()
                or any(part in {"", ".", ".."} for part in raw_path.parts)
                or raw_value in listed_paths
            ):
                manifest_mismatch_count += 1
                continue
            listed_paths.add(raw_value)
            actual_path = bundle / raw_value
            if not _is_regular_no_symlink(actual_path):
                manifest_mismatch_count += 1
                continue
            private_hash_reads += 1
            if (
                row.get("bytes") != actual_path.stat().st_size
                or row.get("sha256") != _sha256_file(actual_path)
            ):
                manifest_mismatch_count += 1
        manifest_mismatch_count += len(LEGACY_MANIFEST_PATHS - listed_paths)
        if _is_regular_no_symlink(bundle / "screenshots" / "terminal.log"):
            terminal_unsealed_count += 1
        if not _is_regular_no_symlink(bundle / "routing.json"):
            routing_unsealed_count += 1
        review_request = bundle / "review_request.md"
        if _is_regular_no_symlink(review_request):
            review_request_text_reads += 1
            try:
                if str(bundle.resolve()) in review_request.read_text(encoding="utf-8"):
                    embedded_absolute_review_count += 1
            except OSError:
                pass

    tracked = _git_tracked_paths(repo_root, review_root)
    tracked_adapter = sum(
        1 for path in adapter_files if path.relative_to(repo_root).as_posix() in tracked
    )
    adapter_symlinks = sum(1 for path in adapter_files if path.is_symlink())
    adapter_owner_only = sum(1 for path in adapter_files if _mode(path) == 0o600)
    return {
        "path_class": "REPO_CONTAINED_SHARED_NAMESPACE",
        "root_mode": _mode(review_root),
        "generic_fixed_basename_file_count": len(generic_files),
        "generic_fixed_basename_mode_histogram": _mode_histogram(generic_files),
        "generic_fixed_basename_symlink_count": generic_symlinks,
        "adapter_bundle_count": len(bundle_dirs),
        "adapter_artifact_file_count": len(adapter_files),
        "adapter_artifact_mode_histogram": _mode_histogram(adapter_files),
        "adapter_artifact_owner_only_count": adapter_owner_only,
        "adapter_artifact_unsafe_count": len(adapter_files) - adapter_owner_only,
        "adapter_artifact_symlink_count": adapter_symlinks,
        "adapter_artifact_tracked_count": tracked_adapter,
        "non_adapter_fixed_basename_file_count": len(generic_files) - len(adapter_files),
        "legacy_manifest_untrusted_bundle_count": len(bundle_dirs),
        "legacy_manifest_mismatch_count": manifest_mismatch_count,
        "terminal_unsealed_bundle_count": terminal_unsealed_count,
        "routing_unsealed_bundle_count": routing_unsealed_count,
        "embedded_absolute_bundle_path_count": embedded_absolute_bundle_count,
        "embedded_absolute_review_path_count": embedded_absolute_review_count,
        "private_artifact_hash_reads": private_hash_reads,
        "manifest_metadata_reads": manifest_metadata_reads,
        "review_request_text_reads": review_request_text_reads,
        "adapter_artifact_hardlink_count": hardlink_count,
        "bundle_symlink_component_count": bundle_symlink_component_count,
        "owner_only": False,
        "status": "SHARED_REPO_NAMESPACE_AND_LEGACY_MANIFEST_UNSAFE",
    }


def _inspect_dispatch_root(repo_root: Path) -> dict[str, Any]:
    root = repo_root / "workbook" / "telegram-dispatch"
    files = [
        path for path in root.rglob("*") if path.is_file() and not path.is_symlink()
    ]
    top_dirs = [
        path for path in root.iterdir() if path.is_dir() and not path.is_symlink()
    ]
    tracked = _git_tracked_paths(repo_root, root)
    tracked_count = sum(
        1 for path in files if path.relative_to(repo_root).as_posix() in tracked
    )
    return {
        "path_class": "REPO_CONTAINED_LIVE_DISPATCH",
        "root_mode": _mode(root),
        "packet_directory_count": len(top_dirs),
        "file_count": len(files),
        "file_mode_histogram": _mode_histogram(files),
        "tracked_file_count": tracked_count,
        "symlink_count": sum(1 for path in root.rglob("*") if path.is_symlink()),
        "launcher_umask_declared_owner_only": False,
        "owner_only": False,
        "status": "LIVE_DISPATCH_REPO_LOCAL_UNSAFE",
    }


def _inspect_backup_propagation(repo_root: Path) -> dict[str, Any]:
    root = Path.home() / "maplab_backup"
    generation_dirs = [
        path
        for path in root.iterdir()
        if path.is_dir() and not path.is_symlink() and path.name.isdigit()
    ] if root.exists() and root.is_dir() and not root.is_symlink() else []
    environment_files: list[Path] = []
    case_store_files: list[Path] = []
    review_fixed_files: list[Path] = []
    adapter_bundle_count = 0
    adapter_artifact_files: list[Path] = []
    dispatch_files: list[Path] = []
    backup_index_files: list[Path] = []
    for generation in generation_dirs:
        for path in generation.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            if path.name == ".env" or (
                path.name.startswith(".env.") and path.name != ".env.example"
            ):
                environment_files.append(path)
        backed_repo = generation / repo_root.name
        for path in backed_repo.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            normalized = path.as_posix()
            if (
                normalized.endswith("/bot_a6/.env")
                or normalized.endswith("/data/case-store/a6_case_store.sqlite3")
                or normalized.endswith("/data/case-store/conversation_log_seed.json")
                or normalized.endswith("/bot_a6/.env.bak")
            ):
                if "/data/case-store/" in normalized:
                    case_store_files.append(path)
            if (
                "/workbook/reviews/" in normalized
                and path.name in OPENCLAW_BUNDLE_FILENAMES
            ):
                review_fixed_files.append(path)
            if "/workbook/telegram-dispatch/" in normalized:
                dispatch_files.append(path)
            if path.name == "dispatch_backup_index.json":
                backup_index_files.append(path)
        review_root = backed_repo / "workbook" / "reviews"
        for manifest_path in review_root.rglob("output_manifest.json"):
            bundle = manifest_path.parent
            if all(_is_regular_no_symlink(bundle / item) for item in ADAPTER_SIGNATURE_PATHS):
                adapter_bundle_count += 1
                adapter_artifact_files.extend(bundle / item for item in ADAPTER_SIGNATURE_PATHS)
    worktree_root = repo_root / ".claude" / "worktrees"
    stale_worktree_copies = [
        path
        for path in worktree_root.rglob(".env.bak")
        if path.is_file() and not path.is_symlink()
    ] if worktree_root.exists() else []
    return {
        "path_class": "OWNER_HOME_EXTERNAL_BUT_MODE_UNSAFE",
        "root_mode": _mode(root),
        "generation_count": len(generation_dirs),
        "environment_copy_count": len(environment_files),
        "environment_copy_mode_histogram": _mode_histogram(environment_files),
        "case_store_copy_count": len(case_store_files),
        "case_store_copy_mode_histogram": _mode_histogram(case_store_files),
        "review_fixed_basename_copy_count": len(review_fixed_files),
        "review_fixed_basename_copy_mode_histogram": _mode_histogram(review_fixed_files),
        "adapter_bundle_copy_count": adapter_bundle_count,
        "adapter_artifact_copy_count": len(adapter_artifact_files),
        "adapter_artifact_copy_mode_histogram": _mode_histogram(adapter_artifact_files),
        "dispatch_file_copy_count": len(dispatch_files),
        "dispatch_file_copy_mode_histogram": _mode_histogram(dispatch_files),
        "backup_index_copy_count": len(backup_index_files),
        "backup_index_copy_mode_histogram": _mode_histogram(backup_index_files),
        "classified_private_copy_count": (
            len(environment_files)
            + len(case_store_files)
            + len(review_fixed_files)
            + len(dispatch_files)
            + len(backup_index_files)
        ),
        "stale_worktree_copy_count": len(stale_worktree_copies),
        "stale_worktree_copy_mode_histogram": _mode_histogram(stale_worktree_copies),
        "owner_only": False,
        "status": "SCHEDULED_REPROPAGATION_UNSAFE",
    }


def inspect_current_modes(repo_root: Path) -> dict[str, Any]:
    case_root = repo_root / "data" / "case-store"
    case_db = case_root / "a6_case_store.sqlite3"
    case_fallback = case_root / "conversation_log_seed.json"
    bot_root = repo_root / "bot_a6"
    bot_env = bot_root / ".env"
    shared_token_parent = Path.home() / ".claude" / "mcp-keys"
    shared_token_grandparent = shared_token_parent.parent
    shared_token = shared_token_parent / ("google-" + "token.json")
    clasp_credential = Path.home() / ".clasprc.json"
    free_compute_parent = Path.home() / ".maplab"
    free_compute_env = free_compute_parent / "free_compute.env"
    hermes_parent = Path.home() / ".hermes"
    hermes_env = hermes_parent / ".env"
    training_root = Path.home() / ".maplab" / "a6-hermes-training"
    training_files = [
        path
        for path in training_root.rglob("*")
        if path.is_file() and not path.is_symlink()
    ] if training_root.is_dir() and not training_root.is_symlink() else []
    training_directories = [
        path
        for path in training_root.rglob("*")
        if path.is_dir() and not path.is_symlink()
    ] if training_root.is_dir() and not training_root.is_symlink() else []
    training_symlink_count = sum(
        1 for path in training_root.rglob("*") if path.is_symlink()
    ) if training_root.is_dir() and not training_root.is_symlink() else 0
    temp_clipboard = Path("/tmp/maplab_clip.json")

    return {
        "case_store": {
            "path_class": "REPO_CONTAINED",
            "directory_mode": _mode(case_root),
            "database_mode": _mode(case_db),
            "fallback_mode": _mode(case_fallback),
            "owner_only": (
                _mode(case_root) == 0o700
                and _mode(case_db) == 0o600
                and _mode(case_fallback) == 0o600
            ),
            "status": "REPO_LOCAL_UNSAFE",
        },
        "bot_env": {
            "path_class": "REPO_CONTAINED",
            "parent_mode": _mode(bot_root),
            "file_present": _is_regular_no_symlink(bot_env),
            "file_mode": _mode(bot_env),
            "owner_only": _mode(bot_root) == 0o700 and _mode(bot_env) == 0o600,
            "status": "REPO_LOCAL_UNSAFE",
        },
        "provider_credential": {
            "path_class": "OWNER_HOME_EXTERNAL_SPLIT_AUTHORITIES",
            "source_parent_mode": _mode(free_compute_parent),
            "source_file_present": _is_regular_no_symlink(free_compute_env),
            "source_file_mode": _mode(free_compute_env),
            "projection_parent_mode": _mode(hermes_parent),
            "projection_file_present": _is_regular_no_symlink(hermes_env),
            "projection_file_mode": _mode(hermes_env),
            "owner_only": (
                _mode(free_compute_parent) == 0o700
                and _mode(free_compute_env) == 0o600
                and _mode(hermes_parent) == 0o700
                and _mode(hermes_env) == 0o600
            ),
            "status": "DUPLICATED_SECRET_AUTHORITIES_AND_SOURCE_PARENT_UNSAFE",
        },
        "hermes_line_training": {
            "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
            "root_mode": _mode(training_root),
            "directory_count": len(training_directories),
            "directory_mode_histogram": _mode_histogram(training_directories),
            "file_count": len(training_files),
            "file_mode_histogram": _mode_histogram(training_files),
            "symlink_count": training_symlink_count,
            "owner_only": False,
            "status": "MODE_ONLY_MATCH_OWNERSHIP_TYPE_ACL_AND_RUNTIME_UNRESOLVED",
        },
        "openclaw_review": _inspect_openclaw_review(repo_root),
        "openclaw_dispatch": _inspect_dispatch_root(repo_root),
        "openclaw_temp_clipboard": {
            "path_class": "SYSTEM_TEMP_HARDCODED",
            "file_present": _is_regular_no_symlink(temp_clipboard),
            "file_mode": _mode(temp_clipboard),
            "owner_only": False,
            "status": "ARCHITECTURE_UNSAFE_CURRENT_FILE_ABSENT",
        },
        "backup_propagation": _inspect_backup_propagation(repo_root),
        "shared_google_credential": {
            "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
            "grandparent_mode": _mode(shared_token_grandparent),
            "parent_mode": _mode(shared_token_parent),
            "file_present": _is_regular_no_symlink(shared_token),
            "file_mode": _mode(shared_token),
            "owner_only": (
                _mode(shared_token_parent) == 0o700
                and _mode(shared_token) == 0o600
            ),
            "status": "EXTERNAL_BUT_MODE_UNSAFE",
        },
        "clasp_credential": {
            "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
            "file_present": _is_regular_no_symlink(clasp_credential),
            "file_mode": _mode(clasp_credential),
            "owner_only": _mode(clasp_credential) == 0o600,
            "status": "UNSAFE_AND_EXCLUDED_FROM_READBACK",
        },
    }


def evaluate_migration_precheck(state: dict[str, Any]) -> str:
    required = {
        "source_snapshot_pinned",
        "target_external_to_repo",
        "target_dir_mode",
        "target_file_mode",
        "target_symlink_free",
        "target_owner_uid_matches",
        "target_regular_types",
        "target_hardlink_free",
        "parent_chain_owner_uid_matches",
        "target_acl_free",
        "consumer_manifest_complete",
        "copy_digest_matches",
        "readback_matches",
        "cutover_cas_matches",
        "rollback_snapshot_preserved",
        "backup_propagation_stopped",
        "actual_byte_ledger_complete",
        "legacy_manifest_used_as_truth",
        "new_writes_external_only",
        "physical_paths_redacted",
        "active_writer_quiesced",
    }
    if set(state) != required:
        return "REJECT_STATE_SHAPE"
    if type(state["source_snapshot_pinned"]) is not bool or not state["source_snapshot_pinned"]:
        return "REJECT_SOURCE_SNAPSHOT"
    if type(state["target_external_to_repo"]) is not bool or not state["target_external_to_repo"]:
        return "REJECT_REPO_TARGET"
    if type(state["target_dir_mode"]) is not int or state["target_dir_mode"] != 0o700:
        return "REJECT_DIRECTORY_MODE"
    if type(state["target_file_mode"]) is not int or state["target_file_mode"] != 0o600:
        return "REJECT_FILE_MODE"
    for key, code in (
        ("target_symlink_free", "REJECT_SYMLINK"),
        ("target_owner_uid_matches", "REJECT_OWNER_UID"),
        ("target_regular_types", "REJECT_NON_REGULAR_TYPE"),
        ("target_hardlink_free", "REJECT_HARDLINK"),
        ("parent_chain_owner_uid_matches", "REJECT_PARENT_OWNER_UID"),
        ("target_acl_free", "REJECT_ACL"),
        ("consumer_manifest_complete", "REJECT_CONSUMER_GAP"),
        ("copy_digest_matches", "REJECT_COPY_DIGEST"),
        ("readback_matches", "REJECT_READBACK"),
        ("cutover_cas_matches", "REJECT_CAS_DRIFT"),
        ("rollback_snapshot_preserved", "REJECT_ROLLBACK_GAP"),
        ("backup_propagation_stopped", "REJECT_BACKUP_PROPAGATION"),
        ("actual_byte_ledger_complete", "REJECT_ACTUAL_BYTE_LEDGER"),
        ("new_writes_external_only", "REJECT_UNSAFE_WRITE_FALLBACK"),
        ("physical_paths_redacted", "REJECT_PHYSICAL_PATH_LEAK"),
        ("active_writer_quiesced", "REJECT_ACTIVE_WRITER"),
    ):
        if type(state[key]) is not bool or not state[key]:
            return code
    if state["legacy_manifest_used_as_truth"] is not False:
        return "REJECT_LEGACY_MANIFEST_TRUST"
    return "PLAN_PRECHECK_PASS"


def evaluate_readback_precheck(state: dict[str, Any]) -> str:
    required = {
        "dedicated_credential",
        "credential_owner_only",
        "credential_symlink_free",
        "scopes",
        "deployment_version_bound",
        "versioned_content_used",
        "raw_source_persisted",
        "raw_identifiers_persisted",
        "write_methods",
        "direct_gas_line_authority",
        "deployment_double_read_stable",
        "target_binding_current_verified",
        "transport_get_only",
        "planned_get_calls",
    }
    if set(state) != required:
        return "REJECT_STATE_SHAPE"
    for key, code in (
        ("dedicated_credential", "REJECT_SHARED_CREDENTIAL"),
        ("credential_owner_only", "REJECT_CREDENTIAL_MODE"),
        ("credential_symlink_free", "REJECT_CREDENTIAL_SYMLINK"),
        ("deployment_version_bound", "REJECT_UNBOUND_VERSION"),
        ("versioned_content_used", "REJECT_HEAD_ONLY"),
        ("deployment_double_read_stable", "REJECT_TOCTOU"),
        ("target_binding_current_verified", "REJECT_HISTORICAL_TARGET"),
        ("transport_get_only", "REJECT_TRANSPORT_METHOD"),
    ):
        if type(state[key]) is not bool or not state[key]:
            return code
    scopes = state["scopes"]
    if not isinstance(scopes, list) or tuple(sorted(scopes)) != tuple(sorted(APPS_SCRIPT_READONLY_SCOPES)):
        return "REJECT_SCOPE_SET"
    if state["raw_source_persisted"] is not False:
        return "REJECT_RAW_SOURCE_PERSISTENCE"
    if state["raw_identifiers_persisted"] is not False:
        return "REJECT_RAW_IDENTIFIER_PERSISTENCE"
    if state["write_methods"] != []:
        return "REJECT_WRITE_METHOD"
    if type(state["planned_get_calls"]) is not int or state["planned_get_calls"] != 3:
        return "REJECT_READ_CALL_COUNT"
    if state["direct_gas_line_authority"] is not False:
        return "REJECT_DIRECT_GAS_LINE_AUTHORITY"
    return "READBACK_PRECHECK_PASS"


def run_fixture_matrix() -> list[dict[str, str]]:
    migration_base: dict[str, Any] = {
        "source_snapshot_pinned": True,
        "target_external_to_repo": True,
        "target_dir_mode": 0o700,
        "target_file_mode": 0o600,
        "target_symlink_free": True,
        "target_owner_uid_matches": True,
        "target_regular_types": True,
        "target_hardlink_free": True,
        "parent_chain_owner_uid_matches": True,
        "target_acl_free": True,
        "consumer_manifest_complete": True,
        "copy_digest_matches": True,
        "readback_matches": True,
        "cutover_cas_matches": True,
        "rollback_snapshot_preserved": True,
        "backup_propagation_stopped": True,
        "actual_byte_ledger_complete": True,
        "legacy_manifest_used_as_truth": False,
        "new_writes_external_only": True,
        "physical_paths_redacted": True,
        "active_writer_quiesced": True,
    }
    readback_base: dict[str, Any] = {
        "dedicated_credential": True,
        "credential_owner_only": True,
        "credential_symlink_free": True,
        "scopes": list(APPS_SCRIPT_READONLY_SCOPES),
        "deployment_version_bound": True,
        "versioned_content_used": True,
        "raw_source_persisted": False,
        "raw_identifiers_persisted": False,
        "write_methods": [],
        "direct_gas_line_authority": False,
        "deployment_double_read_stable": True,
        "target_binding_current_verified": True,
        "transport_get_only": True,
        "planned_get_calls": 3,
    }
    migration_scenarios: list[tuple[str, dict[str, Any], str]] = [
        ("migration_valid", {}, "PLAN_PRECHECK_PASS"),
        ("source_unpinned", {"source_snapshot_pinned": False}, "REJECT_SOURCE_SNAPSHOT"),
        ("repo_target", {"target_external_to_repo": False}, "REJECT_REPO_TARGET"),
        ("dir_0755", {"target_dir_mode": 0o755}, "REJECT_DIRECTORY_MODE"),
        ("file_0644", {"target_file_mode": 0o644}, "REJECT_FILE_MODE"),
        ("bool_as_mode", {"target_file_mode": True}, "REJECT_FILE_MODE"),
        ("symlink_target", {"target_symlink_free": False}, "REJECT_SYMLINK"),
        ("wrong_owner_uid", {"target_owner_uid_matches": False}, "REJECT_OWNER_UID"),
        ("non_regular_type", {"target_regular_types": False}, "REJECT_NON_REGULAR_TYPE"),
        ("hardlink_alias", {"target_hardlink_free": False}, "REJECT_HARDLINK"),
        ("parent_wrong_owner", {"parent_chain_owner_uid_matches": False}, "REJECT_PARENT_OWNER_UID"),
        ("acl_entry", {"target_acl_free": False}, "REJECT_ACL"),
        ("consumer_gap", {"consumer_manifest_complete": False}, "REJECT_CONSUMER_GAP"),
        ("copy_mismatch", {"copy_digest_matches": False}, "REJECT_COPY_DIGEST"),
        ("readback_mismatch", {"readback_matches": False}, "REJECT_READBACK"),
        ("cas_drift", {"cutover_cas_matches": False}, "REJECT_CAS_DRIFT"),
        ("rollback_missing", {"rollback_snapshot_preserved": False}, "REJECT_ROLLBACK_GAP"),
        ("backup_still_copying", {"backup_propagation_stopped": False}, "REJECT_BACKUP_PROPAGATION"),
        ("no_actual_byte_ledger", {"actual_byte_ledger_complete": False}, "REJECT_ACTUAL_BYTE_LEDGER"),
        ("trust_stale_manifest", {"legacy_manifest_used_as_truth": True}, "REJECT_LEGACY_MANIFEST_TRUST"),
        ("fallback_write_to_repo", {"new_writes_external_only": False}, "REJECT_UNSAFE_WRITE_FALLBACK"),
        ("physical_path_in_receipt", {"physical_paths_redacted": False}, "REJECT_PHYSICAL_PATH_LEAK"),
        ("active_writer", {"active_writer_quiesced": False}, "REJECT_ACTIVE_WRITER"),
    ]
    readback_scenarios: list[tuple[str, dict[str, Any], str]] = [
        ("readback_valid", {}, "READBACK_PRECHECK_PASS"),
        ("shared_credential", {"dedicated_credential": False}, "REJECT_SHARED_CREDENTIAL"),
        ("credential_0644", {"credential_owner_only": False}, "REJECT_CREDENTIAL_MODE"),
        ("credential_symlink", {"credential_symlink_free": False}, "REJECT_CREDENTIAL_SYMLINK"),
        ("missing_deployment_scope", {"scopes": [APPS_SCRIPT_READONLY_SCOPES[1]]}, "REJECT_SCOPE_SET"),
        ("broad_write_scope", {"scopes": ["https://www.googleapis.com/auth/script.projects"]}, "REJECT_SCOPE_SET"),
        ("unbound_version", {"deployment_version_bound": False}, "REJECT_UNBOUND_VERSION"),
        ("head_only", {"versioned_content_used": False}, "REJECT_HEAD_ONLY"),
        ("persist_source", {"raw_source_persisted": True}, "REJECT_RAW_SOURCE_PERSISTENCE"),
        ("persist_identifier", {"raw_identifiers_persisted": True}, "REJECT_RAW_IDENTIFIER_PERSISTENCE"),
        ("write_method", {"write_methods": ["projects.updateContent"]}, "REJECT_WRITE_METHOD"),
        ("direct_gas_line", {"direct_gas_line_authority": True}, "REJECT_DIRECT_GAS_LINE_AUTHORITY"),
        ("deployment_changed_midread", {"deployment_double_read_stable": False}, "REJECT_TOCTOU"),
        ("historical_target_only", {"target_binding_current_verified": False}, "REJECT_HISTORICAL_TARGET"),
        ("non_get_transport", {"transport_get_only": False}, "REJECT_TRANSPORT_METHOD"),
        ("wrong_read_call_count", {"planned_get_calls": 2}, "REJECT_READ_CALL_COUNT"),
    ]
    rows: list[dict[str, str]] = []
    for name, mutation, expected in migration_scenarios:
        state = dict(migration_base)
        state.update(mutation)
        actual = evaluate_migration_precheck(state)
        rows.append(
            {
                "name": name,
                "family": "migration",
                "expected": expected,
                "actual": actual,
                "result": "PASS" if actual == expected else "FAIL",
            }
        )
    for name, mutation, expected in readback_scenarios:
        state = dict(readback_base)
        state.update(mutation)
        actual = evaluate_readback_precheck(state)
        rows.append(
            {
                "name": name,
                "family": "readback",
                "expected": expected,
                "actual": actual,
                "result": "PASS" if actual == expected else "FAIL",
            }
        )
    return rows


def inspect_prior_inventory() -> dict[str, Any]:
    trusted = _is_regular_no_symlink(PRIOR_INVENTORY_RECEIPT)
    actual = _sha256_file(PRIOR_INVENTORY_RECEIPT) if trusted else None
    body_matches = False
    if trusted:
        try:
            body_matches = (
                json.loads(PRIOR_INVENTORY_RECEIPT.read_text(encoding="utf-8")).get(
                    "deterministic_body_sha256"
                )
                == PINNED_PRIOR_BODY_SHA256
            )
        except (json.JSONDecodeError, OSError):
            body_matches = False
    return {
        "sha256": actual,
        "matches_pinned": actual == PINNED_PRIOR_RECEIPT_SHA256,
        "body_sha256_matches_pinned": body_matches,
        "status": (
            "MATCH"
            if actual == PINNED_PRIOR_RECEIPT_SHA256 and body_matches
            else "DRIFT_OR_MISSING"
        ),
    }


def inspect_implementation_provenance(repo_root: Path) -> list[dict[str, str]]:
    paths = (
        "scripts/maplab_private_root_hardening_plan.py",
        "tests/test_maplab_private_root_hardening_plan.py",
        "docs/margin-private-root-deployed-readback-hardening-plan.md",
    )
    rows: list[dict[str, str]] = []
    for relative in paths:
        path = repo_root / relative
        if not _is_regular_no_symlink(path):
            raise HardeningPlanError("IMPLEMENTATION_ARTIFACT_MISSING")
        rows.append({"path": relative, "sha256": _sha256_file(path)})
    return rows


def build_receipt(repo_root: Path, created_at: str) -> dict[str, Any]:
    source_pins = inspect_source_pins(repo_root)
    consumers = inspect_consumers(repo_root)
    google_consumers = inspect_google_consumers(repo_root)
    private_env_consumers = inspect_private_env_reference_consumers(repo_root)
    runtime_consumers = inspect_external_runtime_consumers()
    modes = inspect_current_modes(repo_root)
    fixtures = run_fixture_matrix()
    prior = inspect_prior_inventory()

    all_sources_match = all(row["matches_pinned"] for row in source_pins)
    all_consumers_match = all(row["anchors_present"] for row in consumers)
    all_consumer_sources_pinned = all(
        item.path in PINNED_SOURCE_SHA256 for item in CONSUMERS
    )
    all_fixtures_pass = all(row["result"] == "PASS" for row in fixtures)
    current_owner_only = all(row["owner_only"] for row in modes.values())
    design_validated = (
        all_sources_match
        and all_consumers_match
        and all_consumer_sources_pinned
        and google_consumers["repo_manifest_complete"]
        and google_consumers["repo_consumers_all_source_pinned"]
        and google_consumers["safe_external_source_verified_count"] == 3
        and google_consumers["secret_config_metadata_only_count"] == 1
        and google_consumers["external_payload_current_verified"] is False
        and google_consumers["live_cutover_consumer_truth_complete"] is False
        and private_env_consumers["repo_manifest_complete"]
        and private_env_consumers["repo_consumers_all_source_pinned"]
        and private_env_consumers["private_payload_reads"] == 0
        and all(row["matches_pinned"] for row in runtime_consumers)
        and all_fixtures_pass
        and prior["status"] == "MATCH"
    )

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "method_version": METHOD_VERSION,
        "method_fingerprint": method_fingerprint(),
        "created_at": created_at,
        "data_class": DATA_CLASS,
        "method_contract": METHOD_CONTRACT,
        "plateau_review": PLATEAU_REVIEW,
        "prior_inventory": prior,
        "source_pins": source_pins,
        "consumer_inventory": consumers,
        "google_credential_consumers": google_consumers,
        "private_env_reference_consumers": private_env_consumers,
        "external_runtime_consumers": runtime_consumers,
        "implementation_provenance": inspect_implementation_provenance(repo_root),
        "current_modes": modes,
        "target_contracts": TARGET_CONTRACTS,
        "deployed_readback_plan": READBACK_PLAN,
        "synthetic_fixtures": fixtures,
        "safety": {
            "local_filesystem_only": True,
            "private_artifact_hash_reads": modes["openclaw_review"][
                "private_artifact_hash_reads"
            ],
            "private_manifest_metadata_reads": modes["openclaw_review"][
                "manifest_metadata_reads"
            ],
            "private_review_request_text_reads": modes["openclaw_review"][
                "review_request_text_reads"
            ],
            "source_file_hash_reads": len(PINNED_SOURCE_SHA256),
            "source_anchor_text_reads": len(CONSUMERS),
            "cli_implementation_provenance_hash_reads": 12,
            "prior_receipt_hash_reads": 1,
            "prior_receipt_metadata_parses": 1,
            "credential_file_metadata_reads": len(EXTERNAL_GOOGLE_TOKEN_CONSUMERS),
            "provider_credential_metadata_reads": 2,
            "training_root_metadata_reads": (
                1
                + modes["hermes_line_training"]["directory_count"]
                + modes["hermes_line_training"]["file_count"]
            ),
            "external_safe_source_hash_reads": 3,
            "external_runtime_config_file_hash_reads": len(EXTERNAL_RUNTIME_CONSUMERS),
            "external_config_payload_parses": 0,
            "version_control_path_query_operations": 4,
            "private_values_emitted": 0,
            "credential_payload_reads": 0,
            "environment_payload_reads": 0,
            "customer_row_reads": 0,
            "network_calls": 0,
            "apps_script_api_calls": 0,
            "live_target_chmod_operations": 0,
            "live_target_copy_operations": 0,
            "live_target_move_operations": 0,
            "live_target_restart_operations": 0,
            "receipt_artifact_replace_operations": 1,
            "receipt_permission_operations": 1,
            "receipt_fsync_operations": 2,
            "receipt_post_write_readbacks": 1,
            "receipt_validation_passes": 3,
            "deployment_writes": 0,
            "credential_writes": 0,
            "google_writes": 0,
            "customer_send": False,
            "price_system_write": False,
            "historical_mutations": 0,
            "new_private_third_party_egress": False,
            "model_calls": 0,
            "confirmed_leakage_amount": 0,
        },
        "decision": {
            "status": (
                "STATIC_DESIGN_INVENTORY_VALIDATED" if design_validated else "HOLD"
            ),
            "adoption_status": "HOLD",
            "design_inventory_validated": design_validated,
            "resolver_copy_ledger_runtime_validated": False,
            "eligible_for_live_change": False,
            "live_migration_performed": False,
            "current_private_roots_owner_only": current_owner_only,
            "current_quote_deployed_truth_resolved": False,
            "current_line_deployed_truth_resolved": False,
            "orders_writer_resolved": False,
            "header_capable_line_ingress_proven": False,
            "next_repair_point": "synthetic-resolver-and-copy-ledger-prototype",
        },
    }
    body = {
        key: value
        for key, value in receipt.items()
        if key not in {"schema_version", "deterministic_body_sha256"}
    }
    receipt["deterministic_body_sha256"] = _sha256_bytes(_canonical_json(body))
    validate_receipt(receipt)
    return receipt


def _require_exact_keys(value: dict[str, Any], expected: set[str], code: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise HardeningPlanError(code)


def _require_zero_int(value: Any, code: str) -> None:
    if type(value) is not int or value != 0:
        raise HardeningPlanError(code)


def _exact_value_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _exact_value_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _exact_value_equal(left, right)
            for left, right in zip(actual, expected)
        )
    return actual == expected


def _iter_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, nested in value.items():
            yield from _iter_string_values(key)
            yield from _iter_string_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_string_values(nested)


def validate_receipt(receipt: dict[str, Any]) -> None:
    top_keys = {
        "schema_version",
        "method_version",
        "method_fingerprint",
        "created_at",
        "data_class",
        "method_contract",
        "plateau_review",
        "prior_inventory",
        "source_pins",
        "consumer_inventory",
        "google_credential_consumers",
        "private_env_reference_consumers",
        "external_runtime_consumers",
        "implementation_provenance",
        "current_modes",
        "target_contracts",
        "deployed_readback_plan",
        "synthetic_fixtures",
        "safety",
        "decision",
        "deterministic_body_sha256",
    }
    _require_exact_keys(receipt, top_keys, "RECEIPT_TOP_ALLOWLIST")
    if receipt["schema_version"] != SCHEMA_VERSION:
        raise HardeningPlanError("SCHEMA_VERSION")
    if receipt["method_version"] != METHOD_VERSION:
        raise HardeningPlanError("METHOD_VERSION")
    if receipt["data_class"] != DATA_CLASS:
        raise HardeningPlanError("DATA_CLASS")
    if receipt["method_fingerprint"] != method_fingerprint():
        raise HardeningPlanError("METHOD_FINGERPRINT")
    if not _exact_value_equal(receipt["method_contract"], METHOD_CONTRACT):
        raise HardeningPlanError("METHOD_CONTRACT")
    if not _exact_value_equal(receipt["plateau_review"], PLATEAU_REVIEW):
        raise HardeningPlanError("PLATEAU_REVIEW")
    try:
        parsed = datetime.fromisoformat(receipt["created_at"])
    except (TypeError, ValueError) as exc:
        raise HardeningPlanError("TIMESTAMP_INVALID") from exc
    if parsed.tzinfo is None or receipt["created_at"] != EXPECTED_CREATED_AT:
        raise HardeningPlanError("TIMESTAMP_CONTRACT")

    prior = receipt["prior_inventory"]
    _require_exact_keys(
        prior,
        {"sha256", "matches_pinned", "body_sha256_matches_pinned", "status"},
        "PRIOR_ALLOWLIST",
    )
    if not _exact_value_equal(prior, {
        "sha256": PINNED_PRIOR_RECEIPT_SHA256,
        "matches_pinned": True,
        "body_sha256_matches_pinned": True,
        "status": "MATCH",
    }):
        raise HardeningPlanError("PRIOR_BOUNDARY")

    source_rows = receipt["source_pins"]
    if not isinstance(source_rows, list) or len(source_rows) != len(PINNED_SOURCE_SHA256):
        raise HardeningPlanError("SOURCE_MANIFEST_COUNT")
    source_paths = [row.get("path") for row in source_rows]
    if len(set(source_paths)) != len(source_paths) or set(source_paths) != set(PINNED_SOURCE_SHA256):
        raise HardeningPlanError("SOURCE_MANIFEST")
    for row in source_rows:
        _require_exact_keys(
            row,
            {"path", "sha256", "matches_pinned", "status"},
            "SOURCE_ROW_ALLOWLIST",
        )
        if (
            row["sha256"] != PINNED_SOURCE_SHA256[row["path"]]
            or row["matches_pinned"] is not True
            or row["status"] != "MATCH"
        ):
            raise HardeningPlanError("SOURCE_BOUNDARY")

    consumer_rows = receipt["consumer_inventory"]
    expected_consumers = {(c.surface, c.path, c.role): len(c.anchors) for c in CONSUMERS}
    if not isinstance(consumer_rows, list) or len(consumer_rows) != len(CONSUMERS):
        raise HardeningPlanError("CONSUMER_MANIFEST_COUNT")
    actual_consumers: dict[tuple[str, str, str], int] = {}
    for row in consumer_rows:
        _require_exact_keys(
            row,
            {"surface", "path", "role", "anchor_count", "anchors_present", "status"},
            "CONSUMER_ROW_ALLOWLIST",
        )
        key = (row["surface"], row["path"], row["role"])
        if key in actual_consumers:
            raise HardeningPlanError("CONSUMER_DUPLICATE")
        if type(row["anchor_count"]) is not int:
            raise HardeningPlanError("CONSUMER_COUNT_TYPE")
        actual_consumers[key] = row["anchor_count"]
        if row["anchors_present"] is not True or row["status"] != "MATCH":
            raise HardeningPlanError("CONSUMER_BOUNDARY")
    if actual_consumers != expected_consumers:
        raise HardeningPlanError("CONSUMER_MANIFEST")

    google = receipt["google_credential_consumers"]
    _require_exact_keys(
        google,
        {
            "repo_reference_count",
            "repo_scan_scope",
            "external_reference_count",
            "total_known_consumer_count",
            "repo_manifest",
            "external_manifest",
            "repo_missing",
            "repo_unexpected",
            "repo_manifest_complete",
            "repo_consumers_all_source_pinned",
            "safe_external_source_count",
            "safe_external_source_verified_count",
            "secret_config_metadata_only_count",
            "external_payload_current_verified",
            "live_cutover_consumer_truth_complete",
        },
        "GOOGLE_CONSUMER_ALLOWLIST",
    )
    if (
        google["repo_scan_scope"] != "git-index-tracked-bot_a6-scripts-tools"
        or
        type(google["repo_reference_count"]) is not int
        or google["repo_reference_count"] != len(GOOGLE_TOKEN_CONSUMERS)
        or type(google["external_reference_count"]) is not int
        or google["external_reference_count"] != len(EXTERNAL_GOOGLE_TOKEN_CONSUMERS)
        or type(google["total_known_consumer_count"]) is not int
        or google["total_known_consumer_count"]
        != len(GOOGLE_TOKEN_CONSUMERS) + len(EXTERNAL_GOOGLE_TOKEN_CONSUMERS)
    ):
        raise HardeningPlanError("GOOGLE_CONSUMER_COUNT")
    if (
        google["repo_missing"] != []
        or google["repo_unexpected"] != []
        or google["repo_manifest_complete"] is not True
        or google["repo_consumers_all_source_pinned"] is not True
        or type(google["safe_external_source_count"]) is not int
        or google["safe_external_source_count"] != 3
        or type(google["safe_external_source_verified_count"]) is not int
        or google["safe_external_source_verified_count"] != 3
        or type(google["secret_config_metadata_only_count"]) is not int
        or google["secret_config_metadata_only_count"] != 1
        or google["external_payload_current_verified"] is not False
        or google["live_cutover_consumer_truth_complete"] is not False
    ):
        raise HardeningPlanError("GOOGLE_CONSUMER_BOUNDARY")
    expected_google_manifest = [
        {"path": path, "role": GOOGLE_TOKEN_CONSUMERS[path]}
        for path in sorted(GOOGLE_TOKEN_CONSUMERS)
    ]
    if not _exact_value_equal(google["repo_manifest"], expected_google_manifest):
        raise HardeningPlanError("GOOGLE_CONSUMER_MANIFEST")
    expected_external = []
    for alias, contract in sorted(EXTERNAL_GOOGLE_TOKEN_CONSUMERS.items()):
        safe_source = contract["payload_class"] == "source_code"
        expected_external.append(
            {
                "alias": alias,
                "role": contract["role"],
                "payload_class": contract["payload_class"],
                "prior_sha256": contract["sha256"],
                "current_sha256": contract["sha256"] if safe_source else None,
                "file_mode": contract["expected_mode"],
                "file_present": True,
                "current_read_mode": "HASH_ONLY_SOURCE_CODE" if safe_source else "NONE",
                "prior_anchor_bound_by_digest": True,
                "metadata_matches": True,
                "matches_pinned": True if safe_source else None,
                "status": (
                    "MATCH"
                    if safe_source
                    else "PRIOR_PIN_MODE_MATCH_SECRET_CONFIG_UNREAD"
                ),
            }
        )
    if not _exact_value_equal(google["external_manifest"], expected_external):
        raise HardeningPlanError("GOOGLE_EXTERNAL_CONSUMER_MANIFEST")

    private_env = receipt["private_env_reference_consumers"]
    _require_exact_keys(
        private_env,
        {
            "repo_reference_count",
            "repo_scan_scope",
            "repo_manifest",
            "repo_missing",
            "repo_unexpected",
            "repo_manifest_complete",
            "repo_consumers_all_source_pinned",
            "private_payload_reads",
        },
        "PRIVATE_ENV_REFERENCE_ALLOWLIST",
    )
    expected_private_env_manifest = [
        {"path": path, "role": PRIVATE_ENV_REFERENCE_CONSUMERS[path]}
        for path in sorted(PRIVATE_ENV_REFERENCE_CONSUMERS)
    ]
    if (
        private_env["repo_scan_scope"]
        != "git-index-tracked-active-python-shell-and-launchd"
        or type(private_env["repo_reference_count"]) is not int
        or private_env["repo_reference_count"]
        != len(PRIVATE_ENV_REFERENCE_CONSUMERS)
        or not _exact_value_equal(
            private_env["repo_manifest"], expected_private_env_manifest
        )
        or private_env["repo_missing"] != []
        or private_env["repo_unexpected"] != []
        or private_env["repo_manifest_complete"] is not True
        or private_env["repo_consumers_all_source_pinned"] is not True
        or type(private_env["private_payload_reads"]) is not int
        or private_env["private_payload_reads"] != 0
    ):
        raise HardeningPlanError("PRIVATE_ENV_REFERENCE_BOUNDARY")

    runtime_rows = receipt["external_runtime_consumers"]
    expected_runtime = [
        {
            "alias": alias,
            "role": contract["role"],
            "sha256": contract["sha256"],
            "file_mode": contract["expected_mode"],
            "matches_pinned": True,
            "runtime_binding_readback": False,
            "status": "INSTALLED_FILE_MATCH_RUNTIME_BINDING_UNRESOLVED",
        }
        for alias, contract in sorted(EXTERNAL_RUNTIME_CONSUMERS.items())
    ]
    if not _exact_value_equal(runtime_rows, expected_runtime):
        raise HardeningPlanError("EXTERNAL_RUNTIME_CONSUMER_BOUNDARY")

    provenance = receipt["implementation_provenance"]
    expected_provenance = inspect_implementation_provenance(
        Path(__file__).resolve().parents[1]
    )
    if not _exact_value_equal(provenance, expected_provenance):
        raise HardeningPlanError("IMPLEMENTATION_PROVENANCE")

    modes = receipt["current_modes"]
    if set(modes) != {
        "case_store",
        "bot_env",
        "provider_credential",
        "hermes_line_training",
        "openclaw_review",
        "openclaw_dispatch",
        "openclaw_temp_clipboard",
        "backup_propagation",
        "shared_google_credential",
        "clasp_credential",
    }:
        raise HardeningPlanError("MODE_SURFACE_SET")
    expected_case = {
        "path_class": "REPO_CONTAINED",
        "directory_mode": 0o755,
        "database_mode": 0o644,
        "fallback_mode": 0o644,
        "owner_only": False,
        "status": "REPO_LOCAL_UNSAFE",
    }
    if not _exact_value_equal(modes["case_store"], expected_case):
        raise HardeningPlanError("CASE_MODE_BOUNDARY")
    expected_bot = {
        "path_class": "REPO_CONTAINED",
        "parent_mode": 0o755,
        "file_present": True,
        "file_mode": 0o644,
        "owner_only": False,
        "status": "REPO_LOCAL_UNSAFE",
    }
    if not _exact_value_equal(modes["bot_env"], expected_bot):
        raise HardeningPlanError("BOT_ENV_MODE_BOUNDARY")
    if not _exact_value_equal(modes["provider_credential"], {
        "path_class": "OWNER_HOME_EXTERNAL_SPLIT_AUTHORITIES",
        "source_parent_mode": 0o755,
        "source_file_present": True,
        "source_file_mode": 0o600,
        "projection_parent_mode": 0o700,
        "projection_file_present": True,
        "projection_file_mode": 0o600,
        "owner_only": False,
        "status": "DUPLICATED_SECRET_AUTHORITIES_AND_SOURCE_PARENT_UNSAFE",
    }):
        raise HardeningPlanError("PROVIDER_CREDENTIAL_MODE_BOUNDARY")
    if not _exact_value_equal(modes["hermes_line_training"], {
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "root_mode": 0o700,
        "directory_count": 4,
        "directory_mode_histogram": {"0700": 4},
        "file_count": 45,
        "file_mode_histogram": {"0600": 45},
        "symlink_count": 0,
        "owner_only": False,
        "status": "MODE_ONLY_MATCH_OWNERSHIP_TYPE_ACL_AND_RUNTIME_UNRESOLVED",
    }):
        raise HardeningPlanError("HERMES_LINE_TRAINING_MODE_BOUNDARY")
    expected_openclaw_review = {
        "path_class": "REPO_CONTAINED_SHARED_NAMESPACE",
        "root_mode": 0o755,
        "generic_fixed_basename_file_count": 405,
        "generic_fixed_basename_mode_histogram": {"0644": 405},
        "generic_fixed_basename_symlink_count": 0,
        "adapter_bundle_count": 44,
        "adapter_artifact_file_count": 352,
        "adapter_artifact_mode_histogram": {"0644": 352},
        "adapter_artifact_owner_only_count": 0,
        "adapter_artifact_unsafe_count": 352,
        "adapter_artifact_symlink_count": 0,
        "adapter_artifact_tracked_count": 352,
        "non_adapter_fixed_basename_file_count": 53,
        "legacy_manifest_untrusted_bundle_count": 44,
        "legacy_manifest_mismatch_count": 116,
        "terminal_unsealed_bundle_count": 44,
        "embedded_absolute_bundle_path_count": 44,
        "embedded_absolute_review_path_count": 44,
        "private_artifact_hash_reads": 264,
        "manifest_metadata_reads": 44,
        "review_request_text_reads": 44,
        "routing_unsealed_bundle_count": 44,
        "adapter_artifact_hardlink_count": 0,
        "bundle_symlink_component_count": 0,
        "owner_only": False,
        "status": "SHARED_REPO_NAMESPACE_AND_LEGACY_MANIFEST_UNSAFE",
    }
    if not _exact_value_equal(modes["openclaw_review"], expected_openclaw_review):
        raise HardeningPlanError("OPENCLAW_MODE_BOUNDARY")
    expected_dispatch = {
        "path_class": "REPO_CONTAINED_LIVE_DISPATCH",
        "root_mode": 0o755,
        "packet_directory_count": 21,
        "file_count": 83,
        "file_mode_histogram": {"0644": 83},
        "tracked_file_count": 43,
        "symlink_count": 0,
        "launcher_umask_declared_owner_only": False,
        "owner_only": False,
        "status": "LIVE_DISPATCH_REPO_LOCAL_UNSAFE",
    }
    if not _exact_value_equal(modes["openclaw_dispatch"], expected_dispatch):
        raise HardeningPlanError("OPENCLAW_DISPATCH_BOUNDARY")
    if not _exact_value_equal(modes["openclaw_temp_clipboard"], {
        "path_class": "SYSTEM_TEMP_HARDCODED",
        "file_present": False,
        "file_mode": None,
        "owner_only": False,
        "status": "ARCHITECTURE_UNSAFE_CURRENT_FILE_ABSENT",
    }):
        raise HardeningPlanError("OPENCLAW_TEMP_CLIPBOARD_BOUNDARY")
    expected_backup = {
        "path_class": "OWNER_HOME_EXTERNAL_BUT_MODE_UNSAFE",
        "root_mode": 0o755,
        "generation_count": 8,
        "environment_copy_count": 48,
        "environment_copy_mode_histogram": {"0644": 48},
        "case_store_copy_count": 16,
        "case_store_copy_mode_histogram": {"0644": 16},
        "review_fixed_basename_copy_count": 3240,
        "review_fixed_basename_copy_mode_histogram": {"0644": 3240},
        "adapter_bundle_copy_count": 352,
        "adapter_artifact_copy_count": 2816,
        "adapter_artifact_copy_mode_histogram": {"0644": 2816},
        "dispatch_file_copy_count": 600,
        "dispatch_file_copy_mode_histogram": {"0644": 600},
        "backup_index_copy_count": 8,
        "backup_index_copy_mode_histogram": {"0644": 8},
        "classified_private_copy_count": 3912,
        "stale_worktree_copy_count": 2,
        "stale_worktree_copy_mode_histogram": {"0644": 2},
        "owner_only": False,
        "status": "SCHEDULED_REPROPAGATION_UNSAFE",
    }
    if not _exact_value_equal(modes["backup_propagation"], expected_backup):
        raise HardeningPlanError("BACKUP_PROPAGATION_BOUNDARY")
    expected_google_mode = {
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "grandparent_mode": 0o755,
        "parent_mode": 0o755,
        "file_present": True,
        "file_mode": 0o644,
        "owner_only": False,
        "status": "EXTERNAL_BUT_MODE_UNSAFE",
    }
    if not _exact_value_equal(modes["shared_google_credential"], expected_google_mode):
        raise HardeningPlanError("GOOGLE_MODE_BOUNDARY")
    if not _exact_value_equal(modes["clasp_credential"], {
        "path_class": "OWNER_HOME_EXTERNAL_TO_REPO",
        "file_present": True,
        "file_mode": 0o644,
        "owner_only": False,
        "status": "UNSAFE_AND_EXCLUDED_FROM_READBACK",
    }):
        raise HardeningPlanError("CLASP_MODE_BOUNDARY")

    if not _exact_value_equal(receipt["target_contracts"], TARGET_CONTRACTS):
        raise HardeningPlanError("TARGET_CONTRACTS")
    if not _exact_value_equal(receipt["deployed_readback_plan"], READBACK_PLAN):
        raise HardeningPlanError("READBACK_PLAN")

    fixtures = receipt["synthetic_fixtures"]
    expected_fixtures = run_fixture_matrix()
    if not _exact_value_equal(fixtures, expected_fixtures) or len(fixtures) != 39:
        raise HardeningPlanError("FIXTURE_MATRIX")
    if any(row["result"] != "PASS" for row in fixtures):
        raise HardeningPlanError("FIXTURE_FAILURE")

    safety = receipt["safety"]
    _require_exact_keys(
        safety,
        {
            "local_filesystem_only",
            "private_artifact_hash_reads",
            "private_manifest_metadata_reads",
            "private_review_request_text_reads",
            "source_file_hash_reads",
            "source_anchor_text_reads",
            "cli_implementation_provenance_hash_reads",
            "prior_receipt_hash_reads",
            "prior_receipt_metadata_parses",
            "credential_file_metadata_reads",
            "provider_credential_metadata_reads",
            "training_root_metadata_reads",
            "external_safe_source_hash_reads",
            "external_runtime_config_file_hash_reads",
            "external_config_payload_parses",
            "version_control_path_query_operations",
            "private_values_emitted",
            "credential_payload_reads",
            "environment_payload_reads",
            "customer_row_reads",
            "network_calls",
            "apps_script_api_calls",
            "live_target_chmod_operations",
            "live_target_copy_operations",
            "live_target_move_operations",
            "live_target_restart_operations",
            "receipt_artifact_replace_operations",
            "receipt_permission_operations",
            "receipt_fsync_operations",
            "receipt_post_write_readbacks",
            "receipt_validation_passes",
            "deployment_writes",
            "credential_writes",
            "google_writes",
            "customer_send",
            "price_system_write",
            "historical_mutations",
            "new_private_third_party_egress",
            "model_calls",
            "confirmed_leakage_amount",
        },
        "SAFETY_ALLOWLIST",
    )
    if safety["local_filesystem_only"] is not True:
        raise HardeningPlanError("SAFETY_LOCAL_ONLY")
    if (
        type(safety["private_artifact_hash_reads"]) is not int
        or safety["private_artifact_hash_reads"] != 264
        or type(safety["private_manifest_metadata_reads"]) is not int
        or safety["private_manifest_metadata_reads"] != 44
        or type(safety["private_review_request_text_reads"]) is not int
        or safety["private_review_request_text_reads"] != 44
        or type(safety["source_file_hash_reads"]) is not int
        or safety["source_file_hash_reads"] != len(PINNED_SOURCE_SHA256)
        or type(safety["source_anchor_text_reads"]) is not int
        or safety["source_anchor_text_reads"] != len(CONSUMERS)
        or type(safety["cli_implementation_provenance_hash_reads"]) is not int
        or safety["cli_implementation_provenance_hash_reads"] != 12
        or type(safety["prior_receipt_hash_reads"]) is not int
        or safety["prior_receipt_hash_reads"] != 1
        or type(safety["prior_receipt_metadata_parses"]) is not int
        or safety["prior_receipt_metadata_parses"] != 1
        or type(safety["credential_file_metadata_reads"]) is not int
        or safety["credential_file_metadata_reads"]
        != len(EXTERNAL_GOOGLE_TOKEN_CONSUMERS)
        or type(safety["provider_credential_metadata_reads"]) is not int
        or safety["provider_credential_metadata_reads"] != 2
        or type(safety["training_root_metadata_reads"]) is not int
        or safety["training_root_metadata_reads"] != 50
        or type(safety["external_safe_source_hash_reads"]) is not int
        or safety["external_safe_source_hash_reads"] != 3
        or type(safety["external_runtime_config_file_hash_reads"]) is not int
        or safety["external_runtime_config_file_hash_reads"]
        != len(EXTERNAL_RUNTIME_CONSUMERS)
        or type(safety["version_control_path_query_operations"]) is not int
        or safety["version_control_path_query_operations"] != 4
    ):
        raise HardeningPlanError("SAFETY_READ_COUNT")
    for key in (
        "private_values_emitted",
        "credential_payload_reads",
        "environment_payload_reads",
        "external_config_payload_parses",
        "customer_row_reads",
        "network_calls",
        "apps_script_api_calls",
        "live_target_chmod_operations",
        "live_target_copy_operations",
        "live_target_move_operations",
        "live_target_restart_operations",
        "deployment_writes",
        "credential_writes",
        "google_writes",
        "historical_mutations",
        "model_calls",
        "confirmed_leakage_amount",
    ):
        _require_zero_int(safety[key], "SAFETY_ZERO_TYPE_OR_VALUE")
    for key, expected in (
        ("receipt_artifact_replace_operations", 1),
        ("receipt_permission_operations", 1),
        ("receipt_fsync_operations", 2),
        ("receipt_post_write_readbacks", 1),
        ("receipt_validation_passes", 3),
    ):
        if type(safety[key]) is not int or safety[key] != expected:
            raise HardeningPlanError("RECEIPT_WRITE_ACCOUNTING")
    for key in (
        "customer_send",
        "price_system_write",
        "new_private_third_party_egress",
    ):
        if safety[key] is not False:
            raise HardeningPlanError("SAFETY_BOOLEAN")

    decision = receipt["decision"]
    expected_decision = {
        "status": "STATIC_DESIGN_INVENTORY_VALIDATED",
        "adoption_status": "HOLD",
        "design_inventory_validated": True,
        "resolver_copy_ledger_runtime_validated": False,
        "eligible_for_live_change": False,
        "live_migration_performed": False,
        "current_private_roots_owner_only": False,
        "current_quote_deployed_truth_resolved": False,
        "current_line_deployed_truth_resolved": False,
        "orders_writer_resolved": False,
        "header_capable_line_ingress_proven": False,
        "next_repair_point": "synthetic-resolver-and-copy-ledger-prototype",
    }
    if not _exact_value_equal(decision, expected_decision):
        raise HardeningPlanError("DECISION_BOUNDARY")

    serialized = json.dumps(receipt, ensure_ascii=False, sort_keys=True)
    forbidden = (
        '"access_token"',
        '"refresh_token"',
        '"client_secret"',
        '"scriptId"',
        '"deploymentId"',
    )
    if any(value in serialized for value in forbidden):
        raise HardeningPlanError("RECEIPT_SECRET_OR_IDENTIFIER")
    for value in _iter_string_values(receipt):
        if (
            value.startswith("/")
            or "file://" in value.lower()
            or "/Users/" in value
            or "/tmp/" in value
            or "\x00" in value
        ):
            raise HardeningPlanError("RECEIPT_PRIVATE_PATH_OR_URI")

    body = {
        key: value
        for key, value in receipt.items()
        if key not in {"schema_version", "deterministic_body_sha256"}
    }
    expected_body = _sha256_bytes(_canonical_json(body))
    if receipt["deterministic_body_sha256"] != expected_body:
        raise HardeningPlanError("BODY_SHA256")


def _reject_symlink_components(path: Path) -> None:
    current = path
    while True:
        if current.is_symlink():
            raise HardeningPlanError("RECEIPT_SYMLINK")
        if current.parent == current:
            break
        current = current.parent


def write_private_receipt(path: Path, receipt: dict[str, Any]) -> None:
    validate_receipt(receipt)
    if not path.is_absolute():
        raise HardeningPlanError("RECEIPT_PATH_NOT_ABSOLUTE")
    if path.parent != PRIVATE_RECEIPT_ROOT or path.name in {"", ".", ".."}:
        raise HardeningPlanError("RECEIPT_PATH_OUTSIDE_PRIVATE_ROOT")
    _reject_symlink_components(path)
    parent = path.parent
    if (
        not parent.is_dir()
        or _has_symlink_component(parent)
        or _mode(parent) != 0o700
    ):
        raise HardeningPlanError("RECEIPT_PARENT_UNSAFE")
    parent_stat = os.stat(parent, follow_symlinks=False)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(parent, directory_flags)
    opened_parent_stat = os.fstat(directory_fd)
    if (
        (opened_parent_stat.st_dev, opened_parent_stat.st_ino)
        != (parent_stat.st_dev, parent_stat.st_ino)
        or stat.S_IMODE(opened_parent_stat.st_mode) != 0o700
    ):
        os.close(directory_fd)
        raise HardeningPlanError("RECEIPT_PARENT_CHANGED")
    temp_name = f".{path.name}.{secrets.token_hex(12)}.tmp"
    fd: int | None = None
    try:
        try:
            existing = os.stat(path.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and not stat.S_ISREG(existing.st_mode):
            raise HardeningPlanError("RECEIPT_TARGET_UNSAFE")
        fd = os.open(
            temp_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = None
            json.dump(receipt, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(
            temp_name,
            path.name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
        )
        temp_name = ""
        final_fd = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        try:
            final_stat = os.fstat(final_fd)
            if not stat.S_ISREG(final_stat.st_mode) or stat.S_IMODE(final_stat.st_mode) != 0o600:
                raise HardeningPlanError("RECEIPT_POST_WRITE_MODE")
            with os.fdopen(final_fd, "r", encoding="utf-8") as handle:
                final_fd = -1
                validate_receipt(json.load(handle))
        finally:
            if final_fd >= 0:
                os.close(final_fd)
        os.fsync(directory_fd)
    finally:
        if fd is not None:
            os.close(fd)
        if temp_name:
            try:
                os.unlink(temp_name, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
        os.close(directory_fd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the MAPLAB no-write private-root/readback plan"
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--created-at", default=EXPECTED_CREATED_AT)
    args = parser.parse_args()

    receipt = build_receipt(args.repo_root.resolve(), args.created_at)
    write_private_receipt(args.receipt, receipt)
    summary = {
        "status": receipt["decision"]["status"],
        "adoption_status": receipt["decision"]["adoption_status"],
        "source_pins": len(receipt["source_pins"]),
        "consumer_anchors": len(receipt["consumer_inventory"]),
        "shared_credential_references": receipt["google_credential_consumers"][
            "total_known_consumer_count"
        ],
        "fixture_passed": sum(
            1 for row in receipt["synthetic_fixtures"] if row["result"] == "PASS"
        ),
        "fixture_total": len(receipt["synthetic_fixtures"]),
        "unsafe_surface_count": sum(
            1 for row in receipt["current_modes"].values() if not row["owner_only"]
        ),
        "apps_script_api_calls": receipt["safety"]["apps_script_api_calls"],
        "live_change": receipt["decision"]["eligible_for_live_change"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
