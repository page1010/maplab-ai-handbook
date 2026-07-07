import json
import sys
from pathlib import Path


ROOT = Path("/Users/pagemacmini/maplab-ai-handbook")
sys.path.insert(0, str(ROOT / "bot_a6"))

import bot_a6  # noqa: E402


def test_runtime_status_intent_is_narrow() -> None:
    assert bot_a6._looks_like_runtime_status_request("/status")
    assert bot_a6._looks_like_runtime_status_request("你現在是跑什麼模型")
    assert bot_a6._looks_like_runtime_status_request("A6 runtime 狀態")

    owner_question = (
        "我在這裡請你報價 有訓練到ollama 嗎 "
        "有一天出地端專用迷你模型的做法的時候可以把工作流拿給他用嗎？"
    )
    assert not bot_a6._looks_like_runtime_status_request(owner_question)
    assert bot_a6._looks_like_quote_request("15人有主食高毛利 要英文菜單 有看懂嗎")


def test_takeover_packet_has_operable_handoff() -> None:
    chat_id = -6001
    history = bot_a6._get_history(chat_id)
    history.clear()
    history.append({"role": "user", "content": "請接手 A6 Telegram"})
    history.append({"role": "assistant", "content": "收到，我會先做路由判斷。"})

    packet = bot_a6._render_takeover_packet(chat_id)
    assert "A6 接手包" in packet
    assert "Chrome Telegram Web" in packet
    assert "/takeover" in packet
    assert "請接手 A6 Telegram" in packet


def test_photo_handoff_does_not_expose_raw_claude_failure() -> None:
    text = bot_a6._photo_handoff_text(Path("/tmp/a6-photo.jpg"), "看一下")
    assert "圖片已保存" in text
    assert "/takeover" in text
    assert "找不到 claude" not in text.lower()


def test_localquote_summary_compacts_json_flood() -> None:
    quote_message = "15人有主食高毛利 要英文菜單 有看懂嗎"
    payload = bot_a6.build_sheet_quote_payload(quote_message, user_name="Test")
    assert payload
    long_answer = (
        "A5 草稿\n"
        "```json\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n```\n---\nlocal_model=test"
    )
    compact = bot_a6._prepare_local_quote_answer(
        quote_message=quote_message,
        answer=long_answer,
        sheet_payload=None,
        sheet_first_error="",
        force_local=True,
    )
    assert "A5 Sheet-first 報價試算" in compact
    assert "不寫 Google Sheet" in compact
    assert "```json" not in compact


def run_tests() -> None:
    test_runtime_status_intent_is_narrow()
    test_takeover_packet_has_operable_handoff()
    test_photo_handoff_does_not_expose_raw_claude_failure()
    test_localquote_summary_compacts_json_flood()
    print("✅ A6 Telegram route tests passed.")


if __name__ == "__main__":
    run_tests()
