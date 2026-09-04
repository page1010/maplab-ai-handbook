#!/usr/bin/env python3
"""Render the private A8-FITNESS v0.1 movement MVP.

The renderer creates five 17.5-second vertical movement shorts and a
107.5-second compilation.  Frames are deterministic vector drawings rendered
locally with Pillow.  Each short is encoded once from raw frames; the
compilation uses concat-copy and therefore adds no lossy video generation.

The macOS voice is deliberately recorded as a PRIVATE_MVP_PLACEHOLDER.  It may
not be used for public/commercial distribution.  Public candidates must replace
it with a rights-cleared voice and pass the canonical A8 acceptance gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "workbook/reviews/JOB-A8-SENIOR-FITNESS-MVP-20260901"

FPS = 30
SOURCE_W = 540
SOURCE_H = 960
OUT_W = 1080
OUT_H = 1920
SHORT_SECONDS = 17.5
BOOKEND_SECONDS = 10.0
COMPILATION_SECONDS = 107.5
SAMPLE_RATE = 48_000
BPM = 96
SUNO_VARIANT_A_SHA256 = "7245ce245774c6b52fb40a56cb2cea218dfc82e6e8f6e58e34b678348144cc9f"
SUNO_VARIANT_A_URL = "https://suno.com/song/a7641ee9-b921-46f8-b6a0-ca3f976bbf3c"

# Essential Shorts copy stays left of the right-side action rail and above the
# bottom caption/navigation overlay.  Decorative feet/rings may extend lower,
# but every instruction, timer, safety line, and bridge must fit this box.
SHORTS_SAFE_RIGHT = 430
SHORTS_SAFE_BOTTOM = 820

CREAM = "#F7F3EA"
PAPER = "#FFFDF8"
OLIVE = "#34443B"
SAGE = "#86A58C"
SAGE_DARK = "#557662"
CORAL = "#D66A53"
GOLD = "#D8B15A"
MUTED = "#68746C"
LINE = "#D8D4C8"

FONT_PATHS = (
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
)


@dataclass(frozen=True)
class Move:
    slug: str
    name: str
    target: str
    spoken: str
    cue: str
    downgrade: str
    mode: str


MOVES = (
    Move(
        "01-chair-march",
        "扶椅小踏步",
        "髖部／大腿",
        "手輕扶穩，左右小踏步。身體拉高，腳尖朝前，自然呼吸。跟不上就坐著做。不舒服，立刻停。",
        "左右小踏步｜身體拉高",
        "退階：坐姿輪流抬腳",
        "march",
    ),
    Move(
        "02-chair-side-tap",
        "扶椅側點步",
        "髖外側／大腿外側",
        "手輕扶椅背，腳尖左右小點。重心留在站立腳，膝蓋朝前。點近一點也可以。不舒服就停。",
        "小步側點｜不交叉腳",
        "退階：坐姿側點、縮小距離",
        "side",
    ),
    Move(
        "03-chair-heel-raise",
        "扶椅慢抬踵",
        "小腿／腳踝",
        "手輕扶椅背，腳跟慢抬、慢放。腳掌朝前，不彈、不晃。也可坐著做。不舒服就停。下一段先坐穩。",
        "腳跟慢抬｜慢慢放下",
        "退階：坐姿抬腳跟",
        "heel",
    ),
    Move(
        "04-seated-knee-extension",
        "坐姿輪流伸膝",
        "大腿前側",
        "先暫停，坐穩再開始。輪流把小腿往前伸。吐氣伸、吸氣回，膝蓋別鎖死。也可滑腳跟。不舒服就停。",
        "吐氣伸｜膝蓋不鎖死",
        "退階：腳跟貼地往前滑",
        "knee",
    ),
    Move(
        "05-seated-chest-open",
        "坐姿開胸夾背",
        "上背／肩胛周圍",
        "坐直，雙手往前。吐氣時手肘往後，肘低於肩，肩膀放鬆。縮小幅度也可以。不舒服就停。",
        "手肘往後｜肩膀放鬆",
        "退階：手放腿上、小幅後收",
        "chest",
    ),
)

SAFETY_LINES = (
    "一般運動教育｜非醫療",
    "穩固無輪椅、抵牆｜清空地面",
    "防滑鞋｜依自己速度｜隨時暫停",
)

STOP_CARD_LINES = (
    "胸痛／胸悶／嚴重喘",
    "快暈倒／暈眩／心悸",
    "疼痛或不適 → 立即停止",
    "症狀持續，請尋求",
    "當地緊急醫療協助",
)
STOP_LONG = "症狀持續，請尋求當地緊急醫療協助"


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"required tool missing: {name}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    selected = next((path for path in FONT_PATHS if path.is_file()), None)
    if selected is None:
        raise SystemExit("CJK font not found")
    return ImageFont.truetype(str(selected), size=size, index=index)


F_TITLE = font(43)
F_H1 = font(34)
F_BODY = font(27)
F_CUE = font(30)
F_SMALL = font(21)
F_TINY = font(17)
F_NUMBER = font(66)


def rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str, radius: int = 18, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, fnt: ImageFont.FreeTypeFont, fill: str, max_x: int = 450) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    width = box[2] - box[0]
    draw.text(((max_x - width) / 2, y), text, font=fnt, fill=fill)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and draw.textbbox((0, 0), candidate, font=fnt)[2] > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_checked_stack(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    *,
    x: int,
    y: int,
    max_x: int,
    max_y: int,
    fnt: ImageFont.FreeTypeFont,
    colors: list[str],
    gap: int = 9,
) -> None:
    """Draw text using measured glyph bounds and fail closed on overflow."""
    cursor_y = y
    for index, line in enumerate(lines):
        box = draw.textbbox((x, cursor_y), line, font=fnt)
        if box[2] > max_x or box[3] > max_y:
            raise ValueError(
                f"safe text overflow: line={line!r} bounds={box} safe_max=({max_x},{max_y})"
            )
        draw.text((x, cursor_y), line, font=fnt, fill=colors[min(index, len(colors) - 1)])
        cursor_y = box[3] + gap


def chair(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    seat_y = int(y + 130 * scale)
    draw.line((x, y, x, seat_y), fill=OLIVE, width=max(3, int(7 * scale)))
    draw.line((x, seat_y, x + int(115 * scale), seat_y), fill=OLIVE, width=max(3, int(8 * scale)))
    draw.line((x + int(18 * scale), seat_y, x + int(8 * scale), seat_y + int(165 * scale)), fill=OLIVE, width=max(3, int(7 * scale)))
    draw.line((x + int(100 * scale), seat_y, x + int(110 * scale), seat_y + int(165 * scale)), fill=OLIVE, width=max(3, int(7 * scale)))
    draw.line((x - int(10 * scale), y, x + int(25 * scale), y), fill=SAGE_DARK, width=max(3, int(10 * scale)))


def joint(draw: ImageDraw.ImageDraw, p: tuple[float, float], r: int = 8, color: str = OLIVE) -> None:
    x, y = p
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def limb(draw: ImageDraw.ImageDraw, a: tuple[float, float], b: tuple[float, float], width: int = 14, color: str = OLIVE) -> None:
    draw.line((*a, *b), fill=color, width=width)
    joint(draw, a, max(5, width // 2), color)
    joint(draw, b, max(5, width // 2), color)


def target_ring(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], pulse: float, label_y: int) -> None:
    width = 5 + int(2 * pulse)
    draw.ellipse(box, outline=SAGE, width=width)
    rounded(draw, (34, label_y, 322, label_y + 38), PAPER, 14, outline=SAGE, width=2)
    draw.text((49, label_y + 7), "主要活動區（非診斷）", font=F_TINY, fill=SAGE_DARK)


def floor_line(draw: ImageDraw.ImageDraw, y: int = 772, x1: int = 118, x2: int = 390) -> None:
    """Provide an explicit floor reference for heel/slide regressions."""
    draw.line((x1, y, x2, y), fill=LINE, width=5)
    draw.text((x2 - 42, y + 7), "地面", font=F_TINY, fill=MUTED)


def standing_figure(draw: ImageDraw.ImageDraw, mode: str, phase: float, seated: bool = False) -> tuple[int, int, int, int]:
    if seated:
        return seated_figure(draw, mode, phase)

    cx = 238
    head = (cx, 286)
    shoulder = (cx, 345)
    hip = (cx, 525)
    chair(draw, 355, 345, 0.9)
    draw.ellipse((head[0] - 31, head[1] - 31, head[0] + 31, head[1] + 31), fill=GOLD, outline=OLIVE, width=5)
    limb(draw, shoulder, hip, 20)
    limb(draw, (cx - 4, 365), (342, 435), 13)
    limb(draw, (342, 435), (360, 465), 13)

    wave_value = math.sin(phase * math.tau)
    left_hip = (cx - 10, 520)
    right_hip = (cx + 10, 520)

    if mode == "march":
        active_left = wave_value >= 0
        lift = abs(wave_value) * 72
        left_knee = (cx - 36, 625 - (lift if active_left else 0))
        left_foot = (cx - 40, 750 - (lift * 0.55 if active_left else 0))
        right_knee = (cx + 36, 625 - (lift if not active_left else 0))
        right_foot = (cx + 40, 750 - (lift * 0.55 if not active_left else 0))
        ring = (142, 475, 332, 680)
    elif mode == "side":
        shift = wave_value * 48
        left_knee = (cx - 30 + min(0, shift), 635)
        left_foot = (cx - 42 + min(0, shift * 1.6), 752)
        right_knee = (cx + 30 + max(0, shift), 635)
        right_foot = (cx + 42 + max(0, shift * 1.6), 752)
        ring = (125, 485, 352, 700)
    else:
        # Heel raise is deliberately shown in a three-quarter-like stance:
        # toes stay on the floor reference while both heels visibly lift.
        raise_ratio = (wave_value + 1) / 2
        rise = 38 * raise_ratio
        left_knee = (cx - 30, 632 - rise * 0.18)
        left_foot = (cx - 50, 758 - rise)
        right_knee = (cx + 34, 632 - rise * 0.18)
        right_foot = (cx + 28, 758 - rise)
        ring = (145, 610, 332, 790)

    limb(draw, left_hip, left_knee, 17)
    limb(draw, left_knee, left_foot, 16)
    limb(draw, right_hip, right_knee, 17)
    limb(draw, right_knee, right_foot, 16)
    if mode == "heel":
        floor_line(draw)
        left_toe = (left_foot[0] + 43, 770)
        right_toe = (right_foot[0] + 43, 770)
        draw.line((*left_foot, *left_toe), fill=OLIVE, width=12)
        draw.line((*right_foot, *right_toe), fill=OLIVE, width=12)
        joint(draw, left_foot, 9, CORAL)
        joint(draw, right_foot, 9, CORAL)
        draw.line((left_foot[0] - 22, left_foot[1] + 22, left_foot[0] - 22, left_foot[1] - 18), fill=CORAL, width=5)
        draw.polygon(
            (
                (left_foot[0] - 28, left_foot[1] - 14),
                (left_foot[0] - 16, left_foot[1] - 14),
                (left_foot[0] - 22, left_foot[1] - 27),
            ),
            fill=CORAL,
        )
    else:
        draw.line((left_foot[0] - 18, left_foot[1], left_foot[0] + 14, left_foot[1]), fill=OLIVE, width=12)
        draw.line((right_foot[0] - 14, right_foot[1], right_foot[0] + 18, right_foot[1]), fill=OLIVE, width=12)
    return ring


def seated_figure(draw: ImageDraw.ImageDraw, mode: str, phase: float) -> tuple[int, int, int, int]:
    chair(draw, 195, 430, 1.05)
    cx = 250
    head = (cx, 300)
    shoulder = (cx, 360)
    hip = (cx, 565)
    draw.ellipse((head[0] - 31, head[1] - 31, head[0] + 31, head[1] + 31), fill=GOLD, outline=OLIVE, width=5)
    limb(draw, shoulder, hip, 20)
    wave_value = (math.sin(phase * math.tau) + 1) / 2

    if mode in {"march", "side", "heel"}:
        # Seated safety-base variation for standing movements.
        left_knee = (215, 625)
        right_knee = (300, 625)
        if mode == "march":
            lift = 36 * wave_value
            left_foot = (210, 750 - lift)
            right_foot = (310, 750 - 36 * (1 - wave_value))
            ring = (135, 520, 350, 720)
        elif mode == "side":
            spread = 45 * wave_value
            left_foot = (205 - spread, 750)
            right_foot = (315 + spread, 750)
            ring = (115, 535, 380, 735)
        else:
            rise = 32 * wave_value
            left_foot = (205, 755 - rise)
            right_foot = (315, 755 - rise)
            ring = (140, 650, 355, 790)
        limb(draw, hip, left_knee, 17)
        limb(draw, left_knee, left_foot, 16)
        limb(draw, hip, right_knee, 17)
        limb(draw, right_knee, right_foot, 16)
        if mode == "heel":
            floor_line(draw, 772, 130, 405)
            draw.line((*left_foot, left_foot[0] + 44, 770), fill=OLIVE, width=12)
            draw.line((*right_foot, right_foot[0] + 44, 770), fill=OLIVE, width=12)
            joint(draw, left_foot, 9, CORAL)
            joint(draw, right_foot, 9, CORAL)
        else:
            draw.line((left_foot[0] - 16, left_foot[1], left_foot[0] + 20, left_foot[1]), fill=OLIVE, width=12)
            draw.line((right_foot[0] - 16, right_foot[1], right_foot[0] + 20, right_foot[1]), fill=OLIVE, width=12)
        limb(draw, shoulder, (205, 480), 13)
        limb(draw, shoulder, (300, 480), 13)
        return ring

    if mode == "knee_slide":
        # Regression: heel remains in contact with the visible floor line.
        floor_line(draw, 772, 125, 435)
        slide = 118 * wave_value
        left_knee = (325, 625)
        left_foot = (300 + slide, 768)
        right_knee = (265, 640)
        right_foot = (285, 768)
        limb(draw, hip, left_knee, 18)
        limb(draw, left_knee, left_foot, 17)
        limb(draw, hip, right_knee, 18)
        limb(draw, right_knee, right_foot, 17)
        draw.line((left_foot[0] - 8, 768, left_foot[0] + 32, 768), fill=OLIVE, width=12)
        draw.line((right_foot[0] - 8, 768, right_foot[0] + 32, 768), fill=OLIVE, width=12)
        limb(draw, shoulder, (220, 480), 13)
        limb(draw, shoulder, (285, 480), 13)
        return (235, 540, 445, 735)

    if mode == "knee":
        left_knee = (330, 620)
        extend = 110 * wave_value
        left_foot = (342 + extend, 735 - extend * 0.55)
        right_knee = (265, 640)
        right_foot = (285, 755)
        limb(draw, hip, left_knee, 18)
        limb(draw, left_knee, left_foot, 17)
        limb(draw, hip, right_knee, 18)
        limb(draw, right_knee, right_foot, 17)
        draw.line((left_foot[0] - 8, left_foot[1], left_foot[0] + 28, left_foot[1]), fill=OLIVE, width=12)
        draw.line((right_foot[0] - 8, right_foot[1], right_foot[0] + 28, right_foot[1]), fill=OLIVE, width=12)
        limb(draw, shoulder, (220, 480), 13)
        limb(draw, shoulder, (285, 480), 13)
        return (235, 520, 430, 700)

    # Chest-opening movement, viewed from the front.
    hip_left, hip_right = (225, 565), (275, 565)
    knee_left, knee_right = (205, 655), (310, 655)
    foot_left, foot_right = (195, 760), (320, 760)
    limb(draw, hip_left, knee_left, 17)
    limb(draw, knee_left, foot_left, 16)
    limb(draw, hip_right, knee_right, 17)
    limb(draw, knee_right, foot_right, 16)
    if mode == "chest_rest":
        # Regression frame must literally show both hands resting on thighs.
        limb(draw, (232, 375), (215, 485), 14)
        limb(draw, (215, 485), (218, 585), 13)
        limb(draw, (268, 375), (290, 485), 14)
        limb(draw, (290, 485), (292, 585), 13)
        draw.text((150, 330), "手放腿上", font=F_SMALL, fill=SAGE_DARK)
        return (155, 330, 350, 555)

    # Hands begin in front and elbows travel wide/back.  Inward arrows at the
    # shoulder blades make the intended scapular squeeze unambiguous.
    pull = wave_value
    elbow_left = (205 - 52 * pull, 425)
    elbow_right = (295 + 52 * pull, 425)
    hand_left = (225 - 20 * pull, 455)
    hand_right = (275 + 20 * pull, 455)
    limb(draw, (232, 375), elbow_left, 14)
    limb(draw, elbow_left, hand_left, 13)
    limb(draw, (268, 375), elbow_right, 14)
    limb(draw, elbow_right, hand_right, 13)
    if pull > 0.45:
        draw.line((178, 390, 220, 390), fill=CORAL, width=5)
        draw.polygon(((218, 383), (218, 397), (231, 390)), fill=CORAL)
        draw.line((322, 390, 280, 390), fill=CORAL, width=5)
        draw.polygon(((282, 383), (282, 397), (269, 390)), fill=CORAL)
        draw.text((205, 332), "夾背", font=F_SMALL, fill=CORAL)
    return (125, 330, 375, 535)


def base_frame() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (SOURCE_W, SOURCE_H), CREAM)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 540, 18), fill=SAGE)
    draw.rectangle((452, 18, 540, 960), fill="#F0ECE2")
    draw.line((452, 18, 452, 960), fill=LINE, width=2)
    return image, draw


def draw_move_frame(move: Move, t: float, index: int) -> Image.Image:
    image, draw = base_frame()
    draw.text((32, 39), f"{index:02d}", font=F_NUMBER, fill=CORAL)
    draw.text((112, 56), move.name, font=F_H1, fill=OLIVE)
    draw.text((114, 101), "低衝擊節奏間歇｜私人 MVP", font=F_SMALL, fill=MUTED)

    # Platform-safe progress: essential timing no longer sits under the bottom
    # caption rail or the right-side Shorts controls.
    progress = min(1.0, max(0.0, t / SHORT_SECONDS))
    draw.rectangle((24, 132, SHORTS_SAFE_RIGHT, 141), fill=LINE)
    draw.rectangle((24, 132, 24 + int(406 * progress), 141), fill=SAGE_DARK)

    if t < 2.5:
        # Safety copy gets an unobstructed first screen; the human figure is
        # intentionally absent so no head/limb can cover any line.
        rounded(draw, (28, 155, SHORTS_SAFE_RIGHT, 326), PAPER, 22, outline=LINE, width=2)
        draw_checked_stack(
            draw,
            [SAFETY_LINES[0]],
            x=48,
            y=174,
            max_x=414,
            max_y=215,
            fnt=F_BODY,
            colors=[CORAL],
        )
        draw_checked_stack(
            draw,
            list(SAFETY_LINES[1:]),
            x=48,
            y=224,
            max_x=414,
            max_y=312,
            fnt=F_SMALL,
            colors=[OLIVE, OLIVE],
            gap=12,
        )
        first_cue = "先暫停，坐穩再開始" if move.mode == "knee" else "先看一遍｜不用急著跟"
        rounded(draw, (36, 350, 422, 418), OLIVE, 18)
        centered(draw, first_cue, 366, F_BODY, PAPER, max_x=458)
        chair(draw, 210, 455, 0.95)
        floor_line(draw, 760, 155, 385)
    elif t < 12.5:
        local_t = t - 2.5
        cycle = (local_t / 2.5) % 1.0
        ring = standing_figure(draw, move.mode, cycle, seated=move.mode in {"knee", "chest"})
        target_ring(draw, ring, (math.sin(local_t * math.tau / 1.25) + 1) / 2, 770)
        cue_text = "超慢示範" if t < 5.0 else move.cue
    elif t < 15.0:
        cycle = ((t - 12.5) / 2.5) % 1.0
        downgrade_mode = {"knee": "knee_slide", "chest": "chest_rest"}.get(move.mode, move.mode)
        ring = standing_figure(draw, downgrade_mode, cycle, seated=True)
        target_ring(draw, ring, 0.4, 770)
        cue_text = move.downgrade
    else:
        standing_figure(draw, move.mode, 0.0, seated=move.mode in {"knee", "chest"})
        if move.mode == "heel":
            rounded(draw, (48, 520, 416, 575), SAGE_DARK, 16)
            draw.text((67, 535), "下一段：先暫停，坐穩再開始", font=F_SMALL, fill=PAPER)
        rounded(draw, (25, 590, 432, SHORTS_SAFE_BOTTOM), PAPER, 20, outline=CORAL, width=3)
        draw_checked_stack(
            draw,
            list(STOP_CARD_LINES),
            x=43,
            y=610,
            max_x=420,
            max_y=806,
            fnt=F_SMALL,
            colors=[CORAL, CORAL, CORAL, OLIVE, OLIVE],
            gap=8,
        )

    if 2.5 <= t < 15.0:
        rounded(draw, (24, 154, SHORTS_SAFE_RIGHT, 238), OLIVE, 18)
        lines = wrap_text(draw, cue_text, F_CUE, 370)
        for line_index, line in enumerate(lines[:2]):
            draw.text((44, 169 + line_index * 34), line, font=F_CUE if len(lines) == 1 else F_BODY, fill=PAPER)
    return image


def draw_bookend_frame(kind: str, t: float) -> Image.Image:
    image, draw = base_frame()
    if kind == "intro":
        centered(draw, "跟著動", 115, F_TITLE, OLIVE)
        centered(draw, "華語樂齡節拍", 170, F_H1, SAGE_DARK)
        centered(draw, "107.5 秒動作教學合輯", 220, F_BODY, CORAL)
        standing_figure(draw, "march", (t / 2.5) % 1.0, seated=False)
        rounded(draw, (28, 625, SHORTS_SAFE_RIGHT, SHORTS_SAFE_BOTTOM), PAPER, 20, outline=LINE, width=2)
        for line_index, line in enumerate(SAFETY_LINES):
            draw.text((47, 646 + line_index * 48), line, font=F_SMALL if line_index else F_BODY, fill=OLIVE if line_index else CORAL)
    else:
        centered(draw, "慢慢回穩", 120, F_TITLE, OLIVE)
        centered(draw, "自然呼吸｜需要就喝水", 180, F_BODY, SAGE_DARK)
        seated_figure(draw, "chest", min(1.0, t / 5.0))
        rounded(draw, (24, 555, 432, SHORTS_SAFE_BOTTOM), PAPER, 20, outline=CORAL, width=3)
        draw_checked_stack(
            draw,
            list(STOP_CARD_LINES),
            x=43,
            y=580,
            max_x=420,
            max_y=806,
            fnt=F_SMALL,
            colors=[CORAL, CORAL, CORAL, OLIVE, OLIVE],
            gap=10,
        )
    draw.rectangle((24, 82, SHORTS_SAFE_RIGHT, 91), fill=LINE)
    draw.rectangle((24, 82, 24 + int(406 * min(1.0, t / BOOKEND_SECONDS)), 91), fill=SAGE_DARK)
    return image


def write_placeholder_beat(path: Path, duration: float, bpm: int = BPM) -> None:
    total = int(duration * SAMPLE_RATE)
    audio = np.zeros(total, dtype=np.float32)
    beat_samples = int(SAMPLE_RATE * 60 / bpm)
    rng = np.random.default_rng(20260901)
    for beat_index, start in enumerate(range(0, total, beat_samples)):
        kick_len = min(int(0.12 * SAMPLE_RATE), total - start)
        if kick_len <= 0:
            break
        time_axis = np.arange(kick_len, dtype=np.float32) / SAMPLE_RATE
        kick = np.sin(2 * np.pi * (78 - 32 * time_axis) * time_axis) * np.exp(-32 * time_axis)
        audio[start : start + kick_len] += 0.30 * kick
        if beat_index % 4 in {1, 3}:
            clap_len = min(int(0.07 * SAMPLE_RATE), total - start)
            noise = rng.normal(0, 1, clap_len).astype(np.float32) * np.exp(-48 * np.arange(clap_len) / SAMPLE_RATE)
            audio[start : start + clap_len] += 0.055 * noise
    # Soft two-note intro and end chime.
    for second, frequency in ((0.25, 523.25), (duration - 0.7, 392.0)):
        start = max(0, int(second * SAMPLE_RATE))
        length = min(int(0.38 * SAMPLE_RATE), total - start)
        if length <= 0:
            continue
        time_axis = np.arange(length, dtype=np.float32) / SAMPLE_RATE
        audio[start : start + length] += 0.06 * np.sin(2 * np.pi * frequency * time_axis) * np.exp(-8 * time_axis)
    audio = np.clip(audio, -0.95, 0.95)
    pcm = (audio * 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm.tobytes())


def available_say_voice() -> str | None:
    say = shutil.which("say")
    if not say:
        return None
    listing = subprocess.run([say, "-v", "?"], check=False, capture_output=True, text=True).stdout
    for candidate in ("Meijia", "Sinji", "Tingting"):
        if any(line.startswith(candidate + " ") for line in listing.splitlines()):
            return candidate
    return None


def synthesize_voice(text: str, path: Path) -> dict[str, str | int | None]:
    say = require_tool("say")
    voice = available_say_voice()
    command = [say]
    if voice:
        command += ["-v", voice]
    command += ["-r", "195", "-o", str(path), text]
    subprocess.run(command, check=True)
    return {
        "engine": "macOS say",
        "voice": voice or "system-default",
        "rate": 195,
        "rights": "PRIVATE_MVP_PLACEHOLDER_ONLY; not cleared for public or commercial use",
    }


def render_segment(
    ffmpeg: str,
    output: Path,
    voice_path: Path,
    music_path: Path,
    duration: float,
    voice_delay_ms: int,
    frame_fn: Callable[[float], Image.Image],
    lineage_path: Path,
    *,
    music_offset_seconds: float = 0.0,
    music_volume: float = 0.30,
    loop_music: bool = False,
) -> None:
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s:v",
        f"{SOURCE_W}x{SOURCE_H}",
        "-r",
        str(FPS),
        "-i",
        "pipe:0",
        "-i",
        str(voice_path),
    ]
    if loop_music:
        command += ["-stream_loop", "-1", "-ss", f"{music_offset_seconds:.3f}"]
    command += [
        "-i",
        str(music_path),
        "-filter_complex",
        (
            f"[1:a]adelay={voice_delay_ms}:all=1,volume=1.55[voice];"
            f"[2:a]volume={music_volume:.3f}[beat];"
            f"[voice][beat]amix=inputs=2:duration=longest:normalize=0,atrim=0:{duration},"
            "asetpts=N/SR/TB,alimiter=limit=0.95[mix]"
        ),
        "-map",
        "0:v:0",
        "-map",
        "[mix]",
        "-vf",
        f"scale={OUT_W}:{OUT_H}:flags=lanczos,format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-profile:v",
        "high",
        "-level:v",
        "4.1",
        "-g",
        "60",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        str(SAMPLE_RATE),
        "-t",
        str(duration),
        "-movflags",
        "+faststart",
        str(output),
    ]
    started = time.monotonic()
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    frame_count = int(round(duration * FPS))
    try:
        for frame_index in range(frame_count):
            frame = frame_fn(frame_index / FPS)
            process.stdin.write(frame.tobytes())
    finally:
        process.stdin.close()
    result = process.wait()
    if result != 0:
        raise RuntimeError(f"ffmpeg exited {result} for {output.name}")
    lineage = {
        "schema_version": "maplab.a8.fitness-mvp-one-pass/v1",
        "output": str(output),
        "duration_seconds": duration,
        "source": "deterministic Pillow vector frames streamed as raw RGB",
        "source_canvas": [SOURCE_W, SOURCE_H],
        "output_canvas": [OUT_W, OUT_H],
        "fps": FPS,
        "no_intermediate_video": True,
        "lossy_video_encode_count": 1,
        "crop": "none",
        "blur_fill": False,
        "audio_inputs": [str(voice_path), str(music_path)],
        "voice_delay_ms": voice_delay_ms,
        "music_sha256": sha256(music_path),
        "music_offset_seconds": round(music_offset_seconds, 3),
        "music_volume": music_volume,
        "music_looped": loop_music,
        "command": command[:-1] + ["<OUTPUT>"],
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "output_sha256": sha256(output),
    }
    lineage_path.write_text(json.dumps(lineage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ffprobe_payload(ffprobe: str, path: Path) -> dict:
    raw = subprocess.check_output(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    return json.loads(raw)


def extract_encoded_samples(ffmpeg: str, move: Move, video: Path, qa_dir: Path) -> list[Path]:
    """Decode QA stills from the actual encoded MP4, never from frame_fn."""
    paths: list[Path] = []
    for label, moment in (("intro", 1.0), ("action", 8.0), ("downgrade", 13.7), ("stop", 16.2)):
        path = qa_dir / f"{move.slug}-{label}.png"
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(video),
                "-ss",
                str(moment),
                "-frames:v",
                "1",
                str(path),
            ],
            check=True,
        )
        paths.append(path)
    return paths


def contact_sheet(sample_groups: list[list[Path]], output: Path) -> None:
    panel_w, panel_h = 270, 480
    canvas = Image.new("RGB", (panel_w * 4, panel_h * len(sample_groups)), "white")
    for row, group in enumerate(sample_groups):
        for col, path in enumerate(group):
            panel = Image.open(path).convert("RGB").resize((panel_w, panel_h), Image.Resampling.LANCZOS)
            canvas.paste(panel, (col * panel_w, row * panel_h))
    canvas.save(output, quality=92)


def plain_full_decode(ffmpeg: str, path: Path) -> dict[str, str | int]:
    """Fully decode encoded audio/video with no timestamp-changing filters."""
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"plain full decode failed for {path.name}: {completed.stderr.strip()}")
    return {
        "path": str(path),
        "sha256": sha256(path),
        "exit_code": completed.returncode,
        "stderr": completed.stderr.strip(),
        "method": "plain ffmpeg full decode to null; no setpts or other filters",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    ffmpeg = require_tool("ffmpeg")
    ffprobe = require_tool("ffprobe")
    out = args.out.resolve()
    render_dir = out / "render"
    qa_dir = out / "qa"
    receipts_dir = out / "receipts"
    audio_dir = out / "audio"
    for directory in (render_dir, qa_dir, receipts_dir, audio_dir):
        directory.mkdir(parents=True, exist_ok=True)

    outputs = [render_dir / f"{move.slug}.mp4" for move in MOVES]
    compilation = render_dir / "a8-fitness-mvp-compilation-107.5s.mp4"
    if not args.overwrite and any(path.exists() for path in [*outputs, compilation]):
        raise SystemExit("render output already exists; pass --overwrite to regenerate")

    suno_path = audio_dir / "suno-variant-a-32s.wav"
    use_suno = suno_path.is_file()
    music_duration = 0.0
    suno_probe: dict | None = None
    if use_suno:
        actual_suno_hash = sha256(suno_path)
        if actual_suno_hash != SUNO_VARIANT_A_SHA256:
            raise SystemExit(
                f"Suno A source hash drift: expected {SUNO_VARIANT_A_SHA256}, got {actual_suno_hash}"
            )
        suno_probe = ffprobe_payload(ffprobe, suno_path)
        music_duration = float(suno_probe["format"]["duration"])
    # 2026-09-04 Owner 回饋（msg）：「有說話但沒有輕音樂」，0.11 幾乎聽不到，調高至可辨識但仍讓旁白清楚的音量。
    music_volume = 0.22 if use_suno else 0.30

    def music_offset(timeline_seconds: float) -> float:
        if not use_suno or music_duration <= 0:
            return 0.0
        return timeline_seconds % music_duration

    voice_receipts: dict[str, dict] = {}
    sample_groups: list[list[Path]] = []
    records: list[dict] = []
    for index, (move, output) in enumerate(zip(MOVES, outputs), start=1):
        voice_path = audio_dir / f"{move.slug}-voice-placeholder.aiff"
        beat_path = audio_dir / f"{move.slug}-beat-placeholder.wav"
        voice_receipts[move.slug] = synthesize_voice(move.spoken, voice_path)
        if use_suno:
            beat_path = suno_path
        else:
            write_placeholder_beat(beat_path, SHORT_SECONDS)
        render_segment(
            ffmpeg,
            output,
            voice_path,
            beat_path,
            SHORT_SECONDS,
            2500,
            lambda second, m=move, i=index: draw_move_frame(m, second, i),
            receipts_dir / f"{move.slug}-lineage.json",
            music_offset_seconds=music_offset(BOOKEND_SECONDS + (index - 1) * SHORT_SECONDS),
            music_volume=music_volume,
            loop_music=use_suno,
        )
        samples = extract_encoded_samples(ffmpeg, move, output, qa_dir)
        sample_groups.append(samples)
        probe = ffprobe_payload(ffprobe, output)
        records.append(
            {
                "kind": "movement_short",
                "move": move.__dict__,
                "path": str(output),
                "sha256": sha256(output),
                "ffprobe": probe,
                "lineage": str(receipts_dir / f"{move.slug}-lineage.json"),
                "acceptance_status": "PRIVATE_MVP_RENDERED_UNVERIFIED",
            }
        )

    intro_voice = audio_dir / "00-intro-voice-placeholder.aiff"
    intro_beat = audio_dir / "00-intro-beat-placeholder.wav"
    intro_path = render_dir / "00-compilation-intro-10s.mp4"
    voice_receipts["compilation_intro"] = synthesize_voice(
        "歡迎跟著動。先把穩固無輪的椅子靠牆，清開腳邊。照自己的速度，隨時可以暫停。",
        intro_voice,
    )
    if use_suno:
        intro_beat = suno_path
    else:
        write_placeholder_beat(intro_beat, BOOKEND_SECONDS)
    render_segment(
        ffmpeg,
        intro_path,
        intro_voice,
        intro_beat,
        BOOKEND_SECONDS,
        700,
        lambda second: draw_bookend_frame("intro", second),
        receipts_dir / "00-compilation-intro-lineage.json",
        music_offset_seconds=music_offset(0.0),
        music_volume=music_volume,
        loop_music=use_suno,
    )

    outro_voice = audio_dir / "99-outro-voice-placeholder.aiff"
    outro_beat = audio_dir / "99-outro-beat-placeholder.wav"
    outro_path = render_dir / "99-compilation-outro-10s.mp4"
    voice_receipts["compilation_outro"] = synthesize_voice(
        "慢慢回穩，自然呼吸，需要就喝水。胸悶、暈眩、異常喘、心悸或疼痛，立即停止。持續胸痛請尋求緊急協助。",
        outro_voice,
    )
    if use_suno:
        outro_beat = suno_path
    else:
        write_placeholder_beat(outro_beat, BOOKEND_SECONDS)
    render_segment(
        ffmpeg,
        outro_path,
        outro_voice,
        outro_beat,
        BOOKEND_SECONDS,
        500,
        lambda second: draw_bookend_frame("outro", second),
        receipts_dir / "99-compilation-outro-lineage.json",
        music_offset_seconds=music_offset(BOOKEND_SECONDS + len(MOVES) * SHORT_SECONDS),
        music_volume=music_volume,
        loop_music=use_suno,
    )

    concat_list = receipts_dir / "compilation-concat.txt"
    concat_sources = [intro_path, *outputs, outro_path]
    concat_list.write_text("".join(f"file '{path.as_posix()}'\n" for path in concat_sources), encoding="utf-8")
    concat_command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(compilation),
    ]
    subprocess.run(concat_command, check=True)
    compilation_probe = ffprobe_payload(ffprobe, compilation)
    compilation_lineage = {
        "schema_version": "maplab.a8.fitness-mvp-compilation/v1",
        "path": str(compilation),
        "sha256": sha256(compilation),
        "expected_duration_seconds": COMPILATION_SECONDS,
        "sources": [{"path": str(path), "sha256": sha256(path)} for path in concat_sources],
        "assembly": "ffmpeg concat demuxer with stream copy",
        "additional_lossy_video_encodes": 0,
        "command": concat_command[:-1] + ["<OUTPUT>"],
        "ffprobe": compilation_probe,
        "acceptance_status": "PRIVATE_MVP_RENDERED_UNVERIFIED",
    }
    (receipts_dir / "compilation-lineage.json").write_text(
        json.dumps(compilation_lineage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    sheet_path = qa_dir / "movement-contact-sheet.jpg"
    contact_sheet(sample_groups, sheet_path)
    encoded_contact_sheet_receipt = {
        "schema_version": "maplab.a8.encoded-contact-sheet/v1",
        "source_rule": "Every still was decoded from the actual encoded movement MP4; frame_fn was not called for QA capture.",
        "moments_seconds": [1.0, 8.0, 13.7, 16.2],
        "sources": [
            {
                "path": str(output),
                "sha256": sha256(output),
                "stills": [
                    {"path": str(path), "sha256": sha256(path)}
                    for path in sample_group
                ],
            }
            for output, sample_group in zip(outputs, sample_groups)
        ],
        "contact_sheet": {"path": str(sheet_path), "sha256": sha256(sheet_path)},
        "status": "ENCODED_OUTPUT_SAMPLES_EXTRACTED",
    }
    (qa_dir / "encoded_contact_sheet_receipt.json").write_text(
        json.dumps(encoded_contact_sheet_receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    decode_records = [plain_full_decode(ffmpeg, path) for path in [*outputs, compilation]]
    decode_receipt = {
        "schema_version": "maplab.a8.fitness-mvp-plain-decode/v1",
        "scope": "five movement shorts plus assembled compilation",
        "files": decode_records,
        "filters": [],
        "setpts_used": False,
        "status": "PLAIN_FULL_DECODE_PASS",
    }
    (qa_dir / "plain_full_decode_validation.json").write_text(
        json.dumps(decode_receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    technical = {
        "schema_version": "maplab.a8.fitness-mvp-technical-validation/v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "expected": {
            "short_count": 5,
            "short_seconds": SHORT_SECONDS,
            "compilation_seconds": COMPILATION_SECONDS,
            "width": OUT_W,
            "height": OUT_H,
            "fps": FPS,
            "video_codec": "h264",
            "audio_codec": "aac",
        },
        "shorts": records,
        "compilation": compilation_lineage,
        "contact_sheet": {
            "path": str(sheet_path),
            "sha256": sha256(sheet_path),
            "source": "actual encoded MP4 frame extraction",
            "receipt": str(qa_dir / "encoded_contact_sheet_receipt.json"),
        },
        "plain_full_decode": {
            "path": str(qa_dir / "plain_full_decode_validation.json"),
            "status": decode_receipt["status"],
            "setpts_used": False,
        },
        "voice": voice_receipts,
        "music": {
            "current": (
                "Suno variant A mixed at volume 0.11 under the placeholder coaching voice"
                if use_suno
                else "deterministic local 96 BPM placeholder beat"
            ),
            "source_path": str(suno_path) if use_suno else None,
            "source_sha256": sha256(suno_path) if use_suno else None,
            "source_duration_seconds": music_duration if use_suno else None,
            "source_overwritten": False,
            "public_rights_status": "MISSING_CURRENT_RECEIPT; PRIVATE_MVP_ONLY",
        },
        "public_release": False,
        "gates": {
            "pt_review": "MISSING",
            "target_age_usability_test": "MISSING",
            "voice_commercial_rights": "MISSING",
            "suno_rights": "MISSING",
            "actual_audio_human_listen": "MISSING",
            "target_device_readback": "MISSING",
            "owner_video_gate": "MISSING",
            "draft_upload": "NOT_AUTHORIZED",
            "publication": "NOT_AUTHORIZED",
        },
        "status": "PRIVATE_MVP_RENDERED_UNVERIFIED",
    }
    (qa_dir / "technical_validation.json").write_text(
        json.dumps(technical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    download_visual = qa_dir / "suno-download-complete.jpg"
    suno_stream = (suno_probe or {}).get("streams", [{}])[0] if use_suno else {}
    final_mix_outputs = [*outputs, compilation]
    audio_rights = {
        "schema_version": "maplab.a8.fitness-audio-rights/v1",
        "job_id": out.name,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "MISSING_PUBLIC_RIGHTS",
        "ok": False,
        "selected_music_candidate": {
            "title": "跟著動｜96 BPM 樂齡節拍｜Instrumental MVP",
            "variant": "A",
            "source_song_url": SUNO_VARIANT_A_URL,
            "download_path": "../audio/suno-variant-a-32s.wav",
            "sha256": sha256(suno_path) if use_suno else "MISSING",
            "duration_seconds": round(music_duration, 3) if use_suno else None,
            "codec": suno_stream.get("codec_name"),
            "sample_rate_hz": int(suno_stream["sample_rate"]) if suno_stream.get("sample_rate") else None,
            "channels": suno_stream.get("channels"),
            "bytes": suno_path.stat().st_size if use_suno else None,
            "source_overwritten": False,
            "download_method": "Chrome visible UI download followed by native macOS Save dialog",
            "download_visual_receipt": {
                "path": "../qa/suno-download-complete.jpg",
                "sha256": sha256(download_visual) if download_visual.is_file() else "MISSING",
            },
            "generation_scope": "one authorized Suno Create produced two private variants; this receipt binds variant A only",
            "human_full_listen": "MISSING",
            "prompt_free_vocal_or_asr_check": "MISSING",
            "final_mix_binding": {
                "status": "PRIVATE_MVP_MIXED_UNVERIFIED" if use_suno else "MISSING",
                "music_volume": music_volume if use_suno else None,
                "outputs": [
                    {"path": str(path), "sha256": sha256(path)} for path in final_mix_outputs
                ] if use_suno else [],
            },
            "verdict": "MIXED_PRIVATE_UNVERIFIED" if use_suno else "DOWNLOADED_UNVERIFIED",
        },
        "suno_account_ui_readback": {
            "readback_date": "2026-09-01",
            "plan": "Pro Annual",
            "renewal_date_shown": "2027-08-25",
            "credits_before_generation_shown": "2480/2500",
            "commercial_use_text_shown": "commercial use rights for new songs made",
            "evidence_boundary": "Account UI readback only. It is not an independent legal determination and does not clear coaching voice or the exact final mixed output.",
            "independent_terms_verification": "MISSING",
            "legal_advice": False,
        },
        "voice": voice_receipts,
        "music": {
            "current_rendered_outputs": technical["music"]["current"],
            "suno_variant_a": "hash-bound private mix candidate" if use_suno else "downloaded candidate; not mixed",
            "commercial_rights_verdict": "UI_READBACK_PRESENT_NOT_INDEPENDENTLY_VERIFIED",
        },
        "publication_authorization": "NOT_AUTHORIZED",
        "upload_authorization": "NOT_AUTHORIZED",
        "rule": "Suno download, account UI readback, and a hash-bound private mix do not clear the macOS placeholder voice, satisfy human listening, or authorize upload/publication. Keep ok=false until every exact-output audio and rights gate is evidence-bound.",
    }
    (receipts_dir / "audio_rights_receipt.json").write_text(
        json.dumps(audio_rights, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": technical["status"], "shorts": [str(p) for p in outputs], "compilation": str(compilation), "qa": str(qa_dir / "technical_validation.json")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
