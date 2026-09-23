import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = REPO_ROOT / "tools" / "hermes_mlx_lab"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "hermes_mlx_smoke"
RECEIPT = (
    REPO_ROOT
    / "reviews"
    / "HERMES-MLX-DISTILLATION-20260901"
    / "install-smoke-receipt.json"
)


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def test_synthetic_dataset_is_valid_chat_jsonl() -> None:
    expected_counts = {"train.jsonl": 8, "valid.jsonl": 2, "test.jsonl": 1}
    all_text = []
    for name, count in expected_counts.items():
        records = _jsonl(FIXTURE_ROOT / name)
        assert len(records) == count
        for record in records:
            roles = [message["role"] for message in record["messages"]]
            assert roles == ["system", "user", "assistant"]
            all_text.extend(message["content"] for message in record["messages"])

    joined = "\n".join(all_text)
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", joined)
    assert not re.search(r"09\d{8}", joined)


def test_bootstrap_pins_runtime_and_separates_storage_classes() -> None:
    bootstrap = (LAB_ROOT / "bootstrap.zsh").read_text()
    assert "mlx-lm==0.31.3" in (LAB_ROOT / "requirements.lock").read_text()
    assert "50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b" in bootstrap
    assert "/Volumes/MacExternal/MAPLAB_PUBLIC_MODELS" in bootstrap
    assert "/Users/pagemacmini/.maplab/a6-hermes-training/mlx" in bootstrap
    assert "production_route=disabled" in bootstrap


def test_smoke_is_offline_synthetic_and_updates_adapter() -> None:
    smoke = (LAB_ROOT / "run_synthetic_smoke.zsh").read_text()
    assert "(deny network*)" in smoke
    assert "HF_HUB_OFFLINE=1" in smoke
    assert "TRANSFORMERS_OFFLINE=1" in smoke
    assert "HF_DATASETS_OFFLINE=1" in smoke
    assert "--mask-prompt" in smoke
    assert "--adapter-path" in smoke
    assert "data=synthetic_only" in smoke
    assert "quality_claim=false" in smoke


def test_receipt_cannot_be_misread_as_quality_or_live_readiness() -> None:
    receipt = json.loads(RECEIPT.read_text())
    assert receipt["status"] == "INFRASTRUCTURE_SMOKE_PASS_QUALITY_NOT_PROVEN"
    assert receipt["live_route_enabled"] is False
    assert receipt["effect_probe"]["adapter_effect_observed"] is True
    assert receipt["effect_probe"]["business_quality_pass"] is False
    assert receipt["privacy"]["private_data_used"] is False
    assert receipt["privacy"]["customer_send"] is False
    assert receipt["privacy"]["third_party_egress"] is False
