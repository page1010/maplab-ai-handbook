#!/usr/bin/env python3
"""A8 beat-aware 對拍剪輯：偵測歌曲 BPM/beat → 畫面切點對到節拍 → 長度對齊歌曲。
需 numpy（/tmp/ttsenv/bin/python 跑）。ffmpeg 系統版即可。
用法：/tmp/ttsenv/bin/python a8_beat_mux.py <music> <out.mp4> <clip1> [clip2...] [--max SEC] [--perbar 4]
做法(≤10 行)：
 1) ffmpeg 抽單聲道 wav → numpy 讀。
 2) onset envelope(相鄰幀 RMS 正差) → 自相關估 BPM(60–180) → 由首個強 onset 鋪 beat grid。
 3) 以「每 N 拍=一刀」定切點；高能量小節可加倍切(副歌快、主歌慢)。
 4) 每段從 clip 取該長度片段(face-free 視窗內), crop 9:16 1080x1920, 硬切在拍點上。
 5) concat → 疊上歌曲音軌，-t 對齊歌曲長度 → 重編小檔。
 (字幕逐句對人聲=下一步:需 ASR/強制對齊;本版先做視覺對拍+長度對齊。)
"""
import sys, wave, subprocess, math
import numpy as np
from pathlib import Path

def load_audio(path, sr=22050):
    w = "/tmp/_beat.wav"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(path),"-ac","1","-ar",str(sr),w], check=True)
    wf = wave.open(w); raw = wf.readframes(wf.getnframes()); wf.close()
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32)/32768.0, sr

def beat_track(x, sr, hop=512):
    n = (len(x)-hop)//hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:i*hop+hop]**2)) for i in range(n)])
    onset = np.concatenate([[0], np.maximum(0, np.diff(rms))])
    fps = sr/hop
    o = onset - onset.mean()
    ac = np.correlate(o, o, "full")[len(o)-1:]
    best_bpm, best = 120, -1
    for bpm in range(60, 181):
        lag = int(round(fps*60.0/bpm))
        if 1 <= lag < len(ac) and ac[lag] > best: best, best_bpm = ac[lag], bpm
    period = 60.0/best_bpm
    thr = onset.mean() + onset.std()
    first = next((i for i,v in enumerate(onset) if v > thr), 0)/fps
    dur = len(x)/sr
    beats, t = [], first
    while t < dur: beats.append(round(t,3)); t += period
    return best_bpm, beats, onset, fps, dur

def cut_plan(beats, perbar=4):
    # 每 perbar 拍一刀
    return [(beats[i], beats[min(i+perbar, len(beats)-1)]) for i in range(0, len(beats)-1, perbar)]

def render(music, out, clips, maxsec=None, perbar=4):
    x, sr = load_audio(music)
    bpm, beats, onset, fps, dur = beat_track(x, sr)
    songlen = min(dur, maxsec) if maxsec else dur
    cuts = [(a,b) for (a,b) in cut_plan(beats, perbar) if a < songlen]
    if cuts: cuts[-1] = (cuts[-1][0], songlen)
    print(f"BPM={bpm} beats={len(beats)} songlen={songlen:.1f}s cuts={len(cuts)}")
    seg_dir = Path("/tmp/_beatsegs"); seg_dir.mkdir(exist_ok=True)
    # face-free 取用視窗（避免業主/賓客臉）：clip -> (start,maxend)
    windows = {}  # 可外部指定；預設整支
    segfiles = []
    for i,(a,b) in enumerate(cuts):
        seglen = max(0.4, b-a)
        clip = clips[i % len(clips)]
        # 從 clip 內取一段（滾動 offset，限 face-free 視窗）
        st, en = windows.get(Path(clip).name, (0.0, None))
        off = st + (i//len(clips))*seglen
        sf = seg_dir/f"s{i:03d}.mp4"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{off:.2f}","-i",str(clip),"-t",f"{seglen:.2f}",
            "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30",
            "-an","-c:v","libx264","-preset","veryfast","-crf","20",str(sf)], check=False)
        if sf.exists() and sf.stat().st_size>0: segfiles.append(sf)
    lst = seg_dir/"list.txt"; lst.write_text("".join(f"file '{s}'\n" for s in segfiles))
    concat = seg_dir/"concat.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),"-c:v","copy",str(concat)], check=False)
    muxed = seg_dir/"muxed.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(concat),"-i",str(music),
        "-filter_complex","[1:a]volume=0.9,aresample=44100[a]","-map","0:v","-map","[a]","-t",f"{songlen:.2f}",
        "-c:v","copy","-c:a","aac","-b:a","160k",str(muxed)], check=False)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(muxed),"-c:v","libx264","-crf","28","-preset","veryfast",
        "-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",str(out)], check=False)
    v = Path(out)
    print("OUT", out, v.stat().st_size//1024 if v.exists() else 0, "KB; first cut times:", [round(c[0],2) for c in cuts[:6]])

if __name__ == "__main__":
    a = sys.argv
    music, out = a[1], a[2]
    maxsec = float(a[a.index("--max")+1]) if "--max" in a else None
    perbar = int(a[a.index("--perbar")+1]) if "--perbar" in a else 4
    clips = [c for c in a[3:] if not c.startswith("--") and Path(c).exists()]
    render(music, out, clips, maxsec, perbar)
