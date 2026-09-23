#!/usr/bin/env python3
"""下游接法：把 Owner 從 Suno 生好的音檔，接進已渲染的『無聲＋IG Soft 字幕』影片，
取代目前 Apple Loops 配樂＋Piper/say TTS 口白 placeholder。
用法：python3 a8_mux_suno.py <silent_captioned.mp4> <suno.mp3> <out.mp4> [--music-db 0.9]
說明：
  1) 先用 a8_enhanced_video_draft.py 產『無聲字幕影片』(a8-short-review-draft.mp4，本來就 -an)。
  2) 這支把 Suno 音檔當唯一音軌鋪上，裁到影片長度，重編小檔(<10MB 便於上傳)。
  3) 之後照常上 YouTube 私人草稿 / 推 Telegram。
"""
import subprocess, sys
from pathlib import Path
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(p)],capture_output=True,text=True).stdout.strip())
def main():
    if len(sys.argv) < 4:
        print("usage: a8_mux_suno.py <silent_captioned.mp4> <suno.mp3> <out.mp4> [--vol 0.9]"); return
    vid, suno, out = sys.argv[1], sys.argv[2], sys.argv[3]
    vol = sys.argv[sys.argv.index("--vol")+1] if "--vol" in sys.argv else "0.9"
    V = dur(vid)
    muxed = str(Path(out).with_suffix(".muxed.mp4"))
    # Suno 音檔當唯一音軌；若比影片短會自然收尾，長則裁到影片長
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",vid,"-i",suno,
        "-filter_complex",f"[1:a]volume={vol},aresample=44100[a]","-map","0:v","-map","[a]",
        "-t",f"{V:.2f}","-c:v","copy","-c:a","aac","-b:a","192k",muxed],check=False)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",muxed,"-c:v","libx264","-crf","28","-preset","veryfast",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",out],check=False)
    Path(muxed).unlink(missing_ok=True)
    print("done", out, Path(out).stat().st_size//1024 if Path(out).exists() else 0, "KB dur", round(V,1))
if __name__ == "__main__": main()
