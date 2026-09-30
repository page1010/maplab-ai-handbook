"""maplab_secrets — 憑證的「唯一住處」讀取器。

規範(硬性):任何程式都不得把權杖、金鑰、密碼寫死在原始碼裡。
值只住在 .env 檔(不進版控),程式執行時才讀。

  住處優先序:①真正的環境變數 ②maplab-ai-handbook/bot/.env ③~/.maplab/*.env

用法:

    from maplab_secrets import get_secret
    BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN")

設計上刻意「找不到就爆掉」,不回空字串——回空字串會讓呼叫端拿著空權杖去打 API,
拿到 401 之後還要花半天查為什麼,而真因只是忘了設 .env。

規範全文=docs/OPERATING_CULTURE.md 原則 11(憑證只有一個住處)。
機器攔截=scripts/secret_commit_gate.sh(pre-commit,擋住任何把值寫回原始碼的 commit)。
"""

import os
import pathlib

_HERE = pathlib.Path(__file__).resolve().parent
_REPO = _HERE.parent

# 只列「本機確實存在的 .env 位置」。新增位置請一併更新 docs/OPERATING_CULTURE.md 原則 11。
_ENV_FILES = [
    _REPO / "bot" / ".env",
    pathlib.Path.home() / ".maplab" / "free_compute.env",
]

_CACHE = None


def _load_env_files():
    vals = {}
    for path in _ENV_FILES:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # 先到先贏:前面的檔優先,後面的檔只補沒有的鍵
            if key and key not in vals:
                vals[key] = val
    return vals


def get_secret(name, default=None):
    """取一個憑證。找不到且沒給 default 就 raise,不回空字串。"""
    global _CACHE
    val = os.environ.get(name)
    if val:
        return val
    if _CACHE is None:
        _CACHE = _load_env_files()
    val = _CACHE.get(name)
    if val:
        return val
    if default is not None:
        return default
    where = " / ".join(str(p) for p in _ENV_FILES)
    raise RuntimeError(
        "缺少憑證 %s。把值寫進 %s 的其中一個(KEY=VALUE 一行一條),"
        "不要寫回原始碼——寫回去會被 pre-commit 閘門擋下"
        "(規範:docs/OPERATING_CULTURE.md 原則 11)。" % (name, where)
    )


def has_secret(name):
    """只問「有沒有」,不取值。用在啟動前的自我檢查。"""
    try:
        get_secret(name)
        return True
    except RuntimeError:
        return False
