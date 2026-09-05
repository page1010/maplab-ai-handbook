#!/usr/bin/env python3
"""Owner-authorized Telegram gateway for the A6 Hermes surface.

The gateway owns Telegram/network credentials. Models receive text only. Any
local execution is routed through a fixed-argv allowlist with durable receipts.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

try:
    from .hermes_capability_runtime import (
        HISTORY_PATH,
        INBOX_ROOT,
        QUARANTINE_ROOT,
        RUNTIME_ROOT,
        ensure_private_dir,
        format_capabilities,
        save_gateway_state,
        write_private_json,
    )
    from .hermes_task_executor import (
        ACTIONS,
        classify,
        completed_deerflow_notifications,
        deerflow_completion_summary,
        execute as execute_task,
        mark_deerflow_notified,
        telegram_summary,
    )
    from .hermes_durable_job_router import (
        SEO_CUSTOMER_SEND_RE,
        durable_completion_summary,
        mark_durable_notified,
        pending_durable_notifications,
    )
except ImportError:  # Direct launchd/script execution.
    from hermes_capability_runtime import (
        HISTORY_PATH,
        INBOX_ROOT,
        QUARANTINE_ROOT,
        RUNTIME_ROOT,
        ensure_private_dir,
        format_capabilities,
        save_gateway_state,
        write_private_json,
    )
    from hermes_task_executor import (
        ACTIONS,
        classify,
        completed_deerflow_notifications,
        deerflow_completion_summary,
        execute as execute_task,
        mark_deerflow_notified,
        telegram_summary,
    )
    from hermes_durable_job_router import (
        SEO_CUSTOMER_SEND_RE,
        durable_completion_summary,
        mark_durable_notified,
        pending_durable_notifications,
    )


BOT_DIR = Path(__file__).resolve().parent
LOG = BOT_DIR / "hermes_gateway.log"
LEGACY_CONV = BOT_DIR / "hermes_conv.json"
RUNBOOK_PATHS = [
    BOT_DIR.parent / "handoff" / "HERMES_TAKEOVER_RUNBOOK_20260825.md",
    Path.home() / ".hermes" / "HERMES_TAKEOVER_RUNBOOK.md",
]
RANKING = Path.home() / "investment-os" / "scripts" / "free_compute" / "ranking.json"
FREE_ENV = Path.home() / ".maplab" / "free_compute.env"
FALLBACK_CHAIN = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "z-ai/glm-5.2:free",
    "minimax/minimax-m3:free",
]
MAX_HISTORY = 12
MAX_REPLY = 3500
MAX_PHOTO_BYTES = 20 * 1024 * 1024
EXECUTE_PREFIXES = ("/do", "執行：", "執行:", "動手：", "動手:")
CAPABILITY_MARKERS = (
    "權限邊界",
    "你能做",
    "能做什麼",
    "有哪些權限",
    "技能表",
    "當前模型",
    "什麼模型",
    "模型名稱",
    "持久記憶",
    "有記憶",
    "無持久記憶",
    "零存取",
)
SECRET_VALUES: set[str] = set()
PROVIDER_PRIVATE_RE = re.compile(
    r"(客訊|客資|客戶(?:資料|對話|訊息|紀錄)|LINE.{0,12}(?:對話|訊息|紀錄)|"
    r"瀏覽器登入態|cookie|secret|token|API\s*key|密碼|金鑰|"
    r"(?<!\d)09\d{8}(?!\d)|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GatewayRoute:
    disposition: str
    request: str | None = None
    reason: str | None = None


def register_secret(value: str | None) -> None:
    if value:
        SECRET_VALUES.add(value)


def _redact(value: str) -> str:
    for secret in SECRET_VALUES:
        value = value.replace(secret, "[REDACTED]")
    return value


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {_redact(msg)}\n"
    LOG.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(LOG, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(line)
    LOG.chmod(0o600)
    print(line, end="", flush=True)


def message_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def load_free_env_key() -> str | None:
    if "OPENROUTER_API_KEY" in os.environ:
        key = os.environ["OPENROUTER_API_KEY"]
        register_secret(key)
        return key
    try:
        for raw in FREE_ENV.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if raw.startswith("OPENROUTER_API_KEY="):
                key = raw.split("=", 1)[1].strip().strip('"')
                register_secret(key)
                return key
    except OSError:
        pass
    return None


def load_chain() -> list[str]:
    try:
        data = json.loads(RANKING.read_text(encoding="utf-8"))
        chain = data.get("use_cases", {}).get("zh_customer_reply_maplabkitchen", [])
        retired = set(data.get("retired", {}))
        chain = [model for model in chain if model not in retired]
        if chain:
            return chain
    except (OSError, ValueError, TypeError):
        pass
    return FALLBACK_CHAIN.copy()


def load_runbook() -> str:
    for path in RUNBOOK_PATHS:
        try:
            return path.read_text(encoding="utf-8")[:9000]
        except OSError:
            continue
    return "(接手手冊讀取失敗；只依 runtime 能力契約與安全白名單回答。)"


def system_prompt(chain: list[str] | None = None) -> str:
    provider_text = " → ".join(chain or load_chain())
    return (
        "你是 Hermes，在 Owner-authorized A6 Telegram gateway 值班。回覆開頭固定標【hermes】；你不是 Fable5，也不冒充其他代理。\n"
        "能力真相：gateway 能回 Telegram、接收照片、保存最近 12 則生成式對話 context，並透過固定 argv 白名單執行有 receipt 的本機讀取/測試。"
        "這不是零存取，但也不是任意 shell 或 SSH。gateway 持有 Telegram 連線，模型看不到 token。"
        f"設定 provider 鏈：{provider_text}；本地 fallback 已停用（Owner 2026-08-30）。不得說模型完全未知。\n"
        "執行規則：當 runtime 能直接查時，不要叫 Owner 開終端機、不要叫 Owner 貼輸出、不要說等 Fable5/Codex 額度。"
        "A6 gateway 沒有 Google Sheets/Drive/GitHub API 直連；不得把缺少直連誇大成所有本機檔案都不能讀。\n"
        "資料規則：手冊中的日期快照只算歷史背景，不能當成今天狀態；current/latest/目前必須以 runtime action 或新 receipt 為準。"
        "未實際讀到檔案內容時，不得聲稱已讀、不得生成股票名單或其他事實。照片目前只會保存與留 receipt，不得假裝看過像素。\n"
        "硬邊界：不下單、不轉帳、不發布 WordPress、不改生產設定或排程、不讀寫金鑰；投資判讀結尾標『研究判斷,非下單指令』。\n"
        "語氣：說人話、直接、短段落。指出做了什麼、證據在哪、下一個可執行動作。\n\n"
        "以下手冊只提供路徑與歷史背景，不覆蓋上述 runtime 能力契約：\n\n"
        + load_runbook()
    )


def tg_call(token: str, method: str, payload: dict | None = None, timeout: int = 60) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload or {}).encode()
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def openrouter_chat(key: str, model: str, messages: list[dict], timeout: int = 120) -> str | None:
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(
            {
                "model": model,
                "messages": messages,
                "max_tokens": 1200,
                "temperature": 0.25,
            }
        ).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode())
    choices = data.get("choices") or []
    if not choices:
        return None
    content = (choices[0].get("message") or {}).get("content")
    return content.strip() if content and content.strip() else None


def initialize_private_runtime() -> None:
    os.umask(0o077)
    for path in (RUNTIME_ROOT, QUARANTINE_ROOT, INBOX_ROOT):
        ensure_private_dir(path)
    for legacy in (LEGACY_CONV, LOG, BOT_DIR / "launchd_stdout.log", BOT_DIR / "launchd_stderr.log"):
        if legacy.exists():
            legacy.chmod(0o600)
    if not HISTORY_PATH.exists() and LEGACY_CONV.exists():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        quarantine = QUARANTINE_ROOT / f"legacy-conversation-{timestamp}.json"
        try:
            old_payload = json.loads(LEGACY_CONV.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            old_payload = {"unreadable_legacy_path": str(LEGACY_CONV)}
        write_private_json(quarantine, old_payload)
        write_private_json(HISTORY_PATH, [])
        log(f"legacy conversation quarantined path={quarantine}")


def load_history() -> list[dict]:
    try:
        payload = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(payload, list):
        return []
    valid = [
        item
        for item in payload
        if isinstance(item, dict)
        and item.get("role") in {"user", "assistant"}
        and isinstance(item.get("content"), str)
    ]
    return valid[-MAX_HISTORY:]


def save_history(history: list[dict]) -> None:
    write_private_json(HISTORY_PATH, history[-MAX_HISTORY:])


def answer(
    key: str | None,
    chain: list[str],
    history: list[dict],
    user_text: str,
) -> tuple[str | None, str | None]:
    if provider_egress_rejection(history, user_text):
        log("provider egress blocked by private-data DLP")
        return None, None
    messages = [{"role": "system", "content": system_prompt(chain)}] + history + [
        {"role": "user", "content": user_text}
    ]
    if key:
        for model in chain:
            try:
                reply = openrouter_chat(key, model, messages)
            except (urllib.error.URLError, OSError, ValueError, TypeError) as exc:
                log(f"model {model} error={type(exc).__name__} status={getattr(exc, 'code', 'n/a')}")
                continue
            if reply:
                log(f"answered provider={model}")
                return reply, model
            log(f"model {model} empty reply")
    else:
        log("openrouter key unavailable")
    # Owner 2026-08-30: 本機 ollama fallback 停用,鏈盡即回報失敗
    log("provider chain exhausted; local fallback disabled")
    return None, None


def is_capability_question(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text).lower()
    return text.strip().startswith("/capabilities") or any(
        re.sub(r"\s+", "", marker).lower() in normalized for marker in CAPABILITY_MARKERS
    )


def strip_bot_mention(text: str, bot_username: str | None) -> str:
    if not bot_username:
        return text.strip()
    return re.sub(rf"@{re.escape(bot_username)}\b", "", text, flags=re.IGNORECASE).strip()


def normalize_command(text: str, bot_username: str | None) -> str:
    if not text.startswith("/") or not bot_username:
        return text
    return re.sub(
        rf"^(/[^\s@]+)@{re.escape(bot_username)}\b",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )


def provider_egress_rejection(history: list[dict], user_text: str) -> str | None:
    candidate = "\n".join(
        [item.get("content", "") for item in history if isinstance(item, dict)] + [user_text]
    )
    if PROVIDER_PRIVATE_RE.search(candidate):
        return "訊息或對話歷史含客資、LINE 對話、登入態、憑證或直接識別資料；不得送模型 provider"
    return None


def is_group_addressed(message: dict, bot_username: str | None, bot_id: int | None) -> bool:
    chat_type = (message.get("chat") or {}).get("type")
    if chat_type == "private":
        return True
    text = (message.get("text") or message.get("caption") or "").strip()
    if bot_username and f"@{bot_username.lower()}" in text.lower():
        return True
    replied_to = (message.get("reply_to_message") or {}).get("from") or {}
    return bool(bot_id and replied_to.get("id") == bot_id)


def route_gateway_text(text: str, history: list[dict] | None = None) -> GatewayRoute:
    for prefix in EXECUTE_PREFIXES:
        if text.startswith(prefix):
            return GatewayRoute("EXECUTE", request=text[len(prefix) :].strip())
    if SEO_CUSTOMER_SEND_RE.search(text):
        return GatewayRoute("REJECT", request=text, reason="gateway 不得執行對客或 LINE 發送")
    action, reason = classify(text)
    if action:
        return GatewayRoute("EXECUTE", request=text)
    if reason and reason != "不在目前的安全動作白名單":
        return GatewayRoute("REJECT", request=text, reason=reason)
    if text in {"/status", "/runtime"}:
        return GatewayRoute("EXECUTE", request="runtime-status")
    if text in {"/signalstatus", "/signals"}:
        return GatewayRoute("EXECUTE", request="signal-status")
    dlp_reason = provider_egress_rejection(history or [], text)
    if dlp_reason:
        return GatewayRoute("REJECT", request=text, reason=dlp_reason)
    # Fall through to CHAT — executor will reject; gateway loop decides
    return GatewayRoute("CHAT")


def extract_action_request(text: str) -> str | None:
    """Compatibility wrapper; the gateway itself uses the typed route."""

    route = route_gateway_text(text)
    return route.request if route.disposition == "EXECUTE" else None


def _private_write_bytes(path: Path, payload: bytes) -> None:
    ensure_private_dir(path.parent)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(payload)
    path.chmod(0o600)


def receive_photo(token: str, message: dict) -> dict:
    photos = message.get("photo") or []
    if not photos:
        raise ValueError("message has no photo")
    photo = max(photos, key=lambda item: (item.get("file_size") or 0, item.get("width") or 0))
    file_result = tg_call(token, "getFile", {"file_id": photo["file_id"]}, timeout=30)
    file_path = (file_result.get("result") or {}).get("file_path")
    if not file_path or ".." in file_path:
        raise ValueError("Telegram getFile returned unsafe path")
    request = urllib.request.Request(f"https://api.telegram.org/file/bot{token}/{file_path}")
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read(MAX_PHOTO_BYTES + 1)
    if len(payload) > MAX_PHOTO_BYTES:
        raise ValueError("photo exceeds 20 MiB gateway limit")
    unique = re.sub(r"[^A-Za-z0-9_-]", "", photo.get("file_unique_id") or "photo")[:32]
    extension = Path(file_path).suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        extension = ".bin"
    message_id = int(message.get("message_id") or 0)
    stem = f"tg-{message_id}-{unique}"
    saved_path = INBOX_ROOT / f"{stem}{extension}"
    if saved_path.exists():
        saved_path = INBOX_ROOT / f"{stem}-{int(time.time())}{extension}"
    _private_write_bytes(saved_path, payload)
    receipt = {
        "schema_version": 1,
        "type": "telegram-photo-receipt",
        "received_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "message_id": message_id,
        "chat_id": (message.get("chat") or {}).get("id"),
        "chat_type": (message.get("chat") or {}).get("type"),
        "owner_user_id": (message.get("from") or {}).get("id"),
        "caption": (message.get("caption") or "")[:1000],
        "file_path": str(saved_path),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    receipt_path = INBOX_ROOT / f"{stem}.receipt.json"
    receipt["receipt_path"] = str(receipt_path)
    write_private_json(receipt_path, receipt)
    return receipt


def photo_summary(receipt: dict) -> str:
    return (
        "【hermes】照片已收到並私密留檔。\n"
        f"大小：{receipt['bytes']} bytes\n"
        f"sha256：{receipt['sha256'][:16]}…\n"
        f"receipt：{receipt['receipt_path']}\n"
        "這版已完成收圖與可追溯保存；尚未把像素交給視覺模型，所以不會假裝看懂照片。"
    )


def start_text(bot_username: str | None) -> str:
    mention = f"@{bot_username}" if bot_username else "@bot"
    return (
        "【hermes】A6 v3 值班中。你只要說成果目標；公開多來源研究、A8 影音與多輪 LINE 訓練會自動建立持久任務，不必背研究指令。\n"
        "任務會跨 session 留 receipt、續跑到可見成果或真正 Owner gate；私密 A8／LINE 內容只留本機，不送 DeerFlow/OpenRouter。\n"
        "也可用 /capabilities、/do repo-status、/do recent-commits、/do a6-self-test。每次執行都有檔案 receipt。\n"
        f"群組內請 {mention} 或回覆我的訊息；Owner 傳照片時會私密保存並回 photo receipt。"
    )


def drain_background_notifications(token: str) -> int:
    sent = 0
    for item in completed_deerflow_notifications():
        response = tg_call(
            token,
            "sendMessage",
            {"chat_id": item["chat_id"], "text": deerflow_completion_summary(item["receipt"])[:MAX_REPLY]},
        )
        message_id = ((response or {}).get("result") or {}).get("message_id")
        mark_deerflow_notified(item["receipt_path"], message_id)
        sent += 1
    for item in pending_durable_notifications():
        response = tg_call(
            token,
            "sendMessage",
            {"chat_id": item["chat_id"], "text": durable_completion_summary(item["job"])[:MAX_REPLY]},
        )
        message_id = ((response or {}).get("result") or {}).get("message_id")
        mark_durable_notified(item["job_path"], message_id)
        sent += 1
    return sent


def handle_membership_update(token: str, update: dict, owner_user_id: int, bot_username: str | None) -> None:
    actor = update.get("from") or {}
    new_status = ((update.get("new_chat_member") or {}).get("status") or "").lower()
    chat = update.get("chat") or {}
    if actor.get("id") != owner_user_id or new_status not in {"member", "administrator"}:
        return
    if chat.get("type") not in {"group", "supergroup"}:
        return
    tg_call(token, "sendMessage", {"chat_id": chat["id"], "text": start_text(bot_username)})


def main() -> None:
    initialize_private_runtime()
    token = os.environ.get("A6_BOT_TOKEN")
    owner = int(os.environ.get("OWNER_USER_ID", "1077768811"))
    if not token:
        log("FATAL: A6_BOT_TOKEN not in env")
        raise SystemExit(1)
    register_secret(token)
    key = load_free_env_key()
    chain = load_chain()
    bot_id = None
    bot_username = None
    try:
        me = (tg_call(token, "getMe", timeout=30).get("result") or {})
        bot_id = me.get("id")
        bot_username = me.get("username")
    except Exception as exc:
        log(f"getMe error={type(exc).__name__}")
    save_gateway_state(chain, bot_username=bot_username)
    log(
        f"gateway start contract=v2 bot=@{bot_username or 'unknown'} chain={chain} "
        f"openrouter_key={'yes' if key else 'missing'}"
    )
    offset = None
    history = load_history()
    while True:
        try:
            delivered = drain_background_notifications(token)
            if delivered:
                log(f"background notifications sent={delivered}")
            params: dict = {"timeout": 50, "allowed_updates": ["message", "my_chat_member"]}
            if offset is not None:
                params["offset"] = offset
            updates = tg_call(token, "getUpdates", params, timeout=70)
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                membership = update.get("my_chat_member")
                if membership:
                    handle_membership_update(token, membership, owner, bot_username)
                    continue
                message = update.get("message") or {}
                chat = message.get("chat") or {}
                sender = message.get("from") or {}
                if sender.get("id") != owner:
                    log(f"ignore non-owner sender={sender.get('id')} chat_type={chat.get('type')}")
                    continue
                if not is_group_addressed(message, bot_username, bot_id):
                    log(f"ignore unaddressed group chat={chat.get('id')}")
                    continue
                chat_id = chat.get("id")
                if message.get("photo"):
                    try:
                        receipt = receive_photo(token, message)
                    except (urllib.error.URLError, OSError, ValueError, TypeError) as exc:
                        log(f"photo receive failed type={type(exc).__name__}")
                        tg_call(
                            token,
                            "sendMessage",
                            {
                                "chat_id": chat_id,
                                "text": (
                                    "【hermes】照片更新已收到，但下載或私密保存失敗。"
                                    f"錯誤類型：{type(exc).__name__}；沒有假稱已留檔，請直接重傳一次。"
                                ),
                            },
                        )
                        continue
                    log(
                        f"photo received chat_type={chat.get('type')} bytes={receipt['bytes']} "
                        f"sha={receipt['sha256'][:12]}"
                    )
                    tg_call(token, "sendMessage", {"chat_id": chat_id, "text": photo_summary(receipt)[:MAX_REPLY]})
                    continue
                text = (message.get("text") or "").strip()
                if not text:
                    continue
                text = strip_bot_mention(text, bot_username)
                text = normalize_command(text, bot_username)
                log(
                    f"owner message chat_type={chat.get('type')} chars={len(text)} "
                    f"sha={message_fingerprint(text)}"
                )
                if text == "/start":
                    tg_call(token, "sendMessage", {"chat_id": chat_id, "text": start_text(bot_username)})
                    continue
                if is_capability_question(text):
                    reply = format_capabilities(chain, ACTIONS.keys())
                    tg_call(token, "sendMessage", {"chat_id": chat_id, "text": reply[:MAX_REPLY]})
                    continue
                route = route_gateway_text(text, history)
                if route.disposition == "EXECUTE":
                    receipt = execute_task(
                        route.request or text,
                        owner,
                        chat_id=chat_id,
                        chat_type=chat.get("type"),
                        openrouter_key=key,
                    )
                    log(
                        f"executor task={receipt['task_id']} status={receipt['status']} "
                        f"action={receipt.get('action')}"
                    )
                    tg_call(token, "sendMessage", {"chat_id": chat_id, "text": telegram_summary(receipt)[:MAX_REPLY]})
                    continue
                if route.disposition == "REJECT":
                    receipt = execute_task(
                        route.request or text,
                        owner,
                        chat_id=chat_id,
                        chat_type=chat.get("type"),
                        openrouter_key=key,
                    )
                    log(
                        f"executor task={receipt['task_id']} status={receipt['status']} "
                        f"action={receipt.get('action')}"
                    )
                    tg_call(token, "sendMessage", {"chat_id": chat_id, "text": telegram_summary(receipt)[:MAX_REPLY]})
                    continue
                # CHAT disposition — handle as general-chat for private, reject for group
                chat_type = chat.get("type")
                if chat_type == "private":
                    # Use general-chat action for free-form conversation in private
                    receipt = execute_task(
                        f"general-chat: {text}",
                        owner,
                        chat_id=chat_id,
                        chat_type=chat_type,
                        openrouter_key=key,
                    )
                    log(
                        f"executor task={receipt['task_id']} status={receipt['status']} "
                        f"action={receipt.get('action')}"
                    )
                    tg_call(token, "sendMessage", {"chat_id": chat_id, "text": telegram_summary(receipt)[:MAX_REPLY]})
                    continue
                # Group chat without @mention/reply should have been filtered earlier,
                # but if it reaches here, treat as unaddressed
                log(f"ignore unaddressed group chat={chat.get('id')}")
                continue
        except KeyboardInterrupt:
            raise
        except Exception:
            log("loop error:\n" + traceback.format_exc())
            time.sleep(10)


if __name__ == "__main__":
    main()
