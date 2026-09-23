#!/usr/bin/env bash
# case_assets_probe.sh — 第 5、6 篇案例稿的素材可達性探針(唯讀,不改任何檔)
#
# 為什麼有這支(任務 #36):
#   兩篇稿的正文都寫完了,卡住的不是文字,是「圖」——轉正、裁臉、轉 webp、上傳取 media ID。
#   但兩篇 front-matter 的 case_folder_abs 寫的都是 `D:\...`,那是 win-01 的碟。
#   在動手規劃之前必須先答一個是非題:**這台 Mac 到底看不看得到那些原始 HEIC?**
#   看得到 → 圖片工可以在 Mac 做完,不必等 win-01 登入。
#   看不到 → 這件事本質上綁在 win-01 上,今天推不到底,要誠實講而不是先做一半。
#
# 紅線遵守:
#   - 只 ls 兩個指定夾,**不對 CloudStorage 做 du / find 全掃**(disk-hog-cloudstorage 教訓)。
#   - 唯讀。不複製、不轉檔、不上傳、不動 Drive 原檔。
#   - 不印出任何客資內容,只印檔名、大小、張數。
set -uo pipefail

DRIVE="$HOME/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟"
ROOT="$DRIVE/2026maplab外燴紀錄"

C05="0729日照中心開幕"
C06="20260627東門教會證婚"

echo "=== 1. Drive 掛載點在不在 ==="
if [ -d "$DRIVE" ]; then
  echo "OK   我的雲端硬碟 掛載存在"
else
  echo "MISS 我的雲端硬碟 不存在 -> Drive 沒掛載,後面全部免談"
  exit 2
fi

if [ -d "$ROOT" ]; then
  echo "OK   2026maplab外燴紀錄 存在"
else
  echo "MISS 2026maplab外燴紀錄 不在預期位置。"
  echo
  echo "--- 雲端硬碟第一層有什麼(只列名字,不遞迴、不做 du/find 全掃)---"
  ls -1 "$DRIVE" 2>/dev/null | head -60
  echo
  echo "--- 第一層裡名字含「外燴」或「maplab」或「紀錄」的 ---"
  ls -1 "$DRIVE" 2>/dev/null | grep -iE '外燴|maplab|紀錄|2026' || echo "(第一層沒有明顯候選,可能在更深一層或根本不在這顆帳號)"
  echo
  echo "--- 往下探一層:候選父夾裡有沒有 2026maplab外燴紀錄 ---"
  FOUND=""
  for cand in "MAPLAB" "外燴照片（擺設）" "外燴 訂單"; do
    [ -d "$DRIVE/$cand" ] || continue
    echo "[$cand] 第一層:"
    ls -1 "$DRIVE/$cand" 2>/dev/null | head -30 | sed 's/^/    /'
    if [ -d "$DRIVE/$cand/2026maplab外燴紀錄" ]; then
      echo "  >>> 命中:$DRIVE/$cand/2026maplab外燴紀錄"
      FOUND="$DRIVE/$cand/2026maplab外燴紀錄"
    fi
    echo
  done
  if [ -n "$FOUND" ]; then
    echo "找到真實路徑 -> $FOUND"
    echo "請把 ROOT 改成這個值後重跑本探針。"
  else
    echo "結論:兩層之內都找不到 2026maplab外燴紀錄。"
    echo "在找到真實路徑之前,#36 的圖片工不動手,也不憑猜測往下做。"
  fi
  exit 2
fi

probe() {
  # $1=案號 $2=夾名 $3=期望張數
  local tag="$1" dir="$ROOT/$2" want="$3"
  echo
  echo "=== $tag  $2 ==="
  if [ ! -d "$dir" ]; then
    echo "MISS 夾不存在 -> 這一篇的圖在 Mac 上拿不到"
    return
  fi
  local heic mov total zero
  heic=$(ls -1 "$dir" 2>/dev/null | grep -ci '\.heic$')
  mov=$(ls -1 "$dir" 2>/dev/null | grep -ciE '\.(mov|mp4)$')
  total=$(ls -1 "$dir" 2>/dev/null | wc -l | tr -d ' ')
  echo "HEIC=$heic (稿內聲稱 $want)  影片=$mov  夾內總檔數=$total"
  [ "$heic" = "$want" ] && echo "OK   張數與稿內一致" || echo "WARN 張數與稿內不一致,交付前要查清楚是誰對"

  # 串流佔位檢查:Drive 串流模式下未下載的檔 size 可能為 0 或極小
  zero=$(find "$dir" -maxdepth 1 -iname '*.heic' -size -100k 2>/dev/null | wc -l | tr -d ' ')
  if [ "$zero" = "0" ]; then
    echo "OK   無疑似串流佔位檔(全部 >100k,是實體檔,讀得到像素)"
  else
    echo "WARN 有 $zero 個 HEIC 小於 100k -> 可能是串流佔位,要先讓 Drive 下載才處理得動"
  fi
}

probe "第5篇 日照中心" "$C05" 7
probe "第6篇 教會證婚" "$C06" 27

echo
echo "=== 4. 圖片工具鏈在不在(決定圖片工能不能在 Mac 做) ==="
for t in sips cwebp; do
  if command -v "$t" >/dev/null 2>&1; then echo "OK   $t"; else echo "MISS $t"; fi
done
# PIL 只有系統 python3 有(agent-hq-and-photo-pipeline 教訓)
if /usr/bin/python3 -c 'import PIL, PIL.Image; print("OK   系統 python3 有 PIL", PIL.__version__)' 2>/dev/null; then :; else
  echo "MISS 系統 python3 無 PIL"
fi

echo
echo "=== 結論怎麼讀 ==="
echo "兩個夾都 OK 且無佔位檔 + sips/cwebp 或 PIL 至少一套在 -> 圖片工可在 Mac 做完,#36 不必等 win-01。"
echo "任一 MISS -> 誠實回報「這件事綁在 win-01 上」,不先做一半再說做不完。"
