#!/usr/bin/env python3
"""local_face_screen.py — 本機人臉篩查(零雲端)

由來:任務卡 #120。週歲抓周那批照片裡有小孩,而長期紅線是
「兒童照片一律不上傳雲端模型」——包含不能丟給我自己(Claude 是雲端模型)看。
於是形成死結:要挑廣告用圖得先看過圖,但看圖這個動作本身就違規。

解法不是放寬紅線,是補一個本機的眼睛:
OpenCV 的 YuNet 人臉偵測器在這台機器上跑,照片全程不離開本機,
只把「這個檔案有幾張臉」這個數字交出來。0 張臉的才准進入後續人工/雲端檢視,
有臉的一律標成「本機處理,不判」,連檔名帶場景都不往外送圖。

這條線只證明「沒有偵測到臉」,不證明「畫面裡沒有小孩」——背影、
被遮住的側臉、只入鏡半截身體都可能漏。所以輸出欄位叫 faces 不叫 safe,
判定權仍在人身上(企業文化原則 12 第四條:不知道的不准當成知道)。

用法:
  <venv>/bin/python scripts/local_face_screen.py <圖片目錄或檔案> [--pattern 子字串] [--csv 輸出路徑]
回傳:全部掃完 exit 0;有檔案讀不進來 exit 1(讀不到不等於沒有臉)。

環境:需要 opencv-python-headless 與 YuNet 權重檔。
  權重 = ~/.maplab/models/face_detection_yunet_2023mar.onnx(公開模型,非客戶資料)
  直譯器 = ~/.maplab/cvenv312/bin/python(系統 python 3.9 裝不了 cv2 5.x)
"""
import csv
import os
import sys

MODEL = os.path.expanduser('~/.maplab/models/face_detection_yunet_2023mar.onnx')
# 0.6 是 YuNet 作者給的預設信心門檻。這裡刻意不調低:調低會多抓到雜訊框,
# 讓「有臉」這個標記變得不值錢,人就會開始忽略它——寧可漏報由人補,不要狼來了。
SCORE_THRESHOLD = 0.6
NMS_THRESHOLD = 0.3
TOP_K = 5000


def detect(det, path):
    import cv2
    img = cv2.imread(path)
    if img is None:
        # webp/HEIC 之類 cv2 讀不動的,退回 PIL 轉成 numpy 再試一次。
        try:
            import numpy as np
            from PIL import Image
            with Image.open(path) as im:
                img = np.array(im.convert('RGB'))[:, :, ::-1].copy()
        except Exception:
            return None, None
    h, w = img.shape[:2]
    det.setInputSize((w, h))
    _, faces = det.detect(img)
    return (0 if faces is None else len(faces)), '%dx%d' % (w, h)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    target = args[0]
    pattern = ''
    out_csv = ''
    if '--pattern' in args:
        pattern = args[args.index('--pattern') + 1]
    if '--csv' in args:
        out_csv = args[args.index('--csv') + 1]

    if not os.path.exists(MODEL):
        print('找不到 YuNet 權重:%s' % MODEL)
        print('取得方式:curl -sSL -o <上述路徑> \\')
        print('  https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx')
        return 2
    try:
        import cv2
    except ImportError:
        print('這個直譯器沒有 cv2。用 ~/.maplab/cvenv312/bin/python 跑。')
        return 2

    if os.path.isdir(target):
        files = [os.path.join(target, f) for f in sorted(os.listdir(target))
                 if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png'))]
    else:
        files = [target]
    if pattern:
        files = [f for f in files if pattern in os.path.basename(f)]

    det = cv2.FaceDetectorYN.create(MODEL, '', (320, 320), SCORE_THRESHOLD, NMS_THRESHOLD, TOP_K)
    rows = []
    unreadable = 0
    for f in files:
        n, size = detect(det, f)
        if n is None:
            unreadable += 1
            rows.append((os.path.basename(f), '讀不到', '', '讀不到就當成有臉,不准進廣告'))
            continue
        rows.append((os.path.basename(f), n, size,
                     '可進人工檢視' if n == 0 else '本機處理,不判——不得上傳雲端模型'))

    w = csv.writer(open(out_csv, 'w', newline='', encoding='utf-8')) if out_csv else None
    if w:
        w.writerow(['檔名', '偵測到的臉數', '尺寸', '處置'])
    zero = sum(1 for r in rows if r[1] == 0)
    for r in rows:
        if w:
            w.writerow(r)
        else:
            print('%-58s 臉=%-6s %-10s %s' % r)
    print('---')
    print('掃描 %d 張:0 張臉 %d、有臉 %d、讀不到 %d' % (
        len(rows), zero, len(rows) - zero - unreadable, unreadable))
    if out_csv:
        print('CSV → %s' % out_csv)
    print('注意:0 張臉只代表「沒有偵測到正面人臉」,不等於畫面裡沒有小孩。判定權在人。')
    return 1 if unreadable else 0


if __name__ == '__main__':
    sys.exit(main())
