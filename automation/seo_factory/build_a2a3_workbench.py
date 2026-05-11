#!/usr/bin/env python3
from __future__ import annotations

import json
import html
import os
import re
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent
from urllib.parse import unquote, urlparse


REPO = Path(__file__).resolve().parents[2]
SCENARIO_JSON = REPO / "automation" / "seo_factory" / "config" / "scenario_pages.json"
DESKTOP_ROOT = Path.home() / "Desktop" / "wordpress 素材庫"

SOURCE_SCENE_DIR = Path.home() / "Desktop" / "wordpress 素材庫" / "source_2025_curated"
SOURCE_FOOD_DIR = Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "食物介紹素材" / "webp"
SOURCE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI/edit?usp=sharing"

PAGE_SPEC = {
    "opening-event-catering-tainan": {
        "budget_range": "15,000–80,000+",
        "person_range": "20–150 人",
        "hero_hook": "開幕茶會不是只上餐點，而是先把品牌第一印象做對。",
        "ad_angle": "診所、醫美、品牌、公司開幕的體面與節奏",
        "cta_line": "先傳活動時段、人數、地點，我們先幫你對齊開幕節奏。",
        "faq_extra": [
            ("開幕茶會和一般派對外燴差在哪？", "開幕茶會更看重品牌體面、來賓動線與接待節奏，不只是餐點而已。"),
            ("診所或醫美開幕也能做嗎？", "可以，會把畫面感、桌面配置與來賓停留時間一起規劃。"),
        ],
        "internal_links": ["meeting-refreshment-catering-tainan", "brand-event-catering", "catering-corporate-tainan"],
    },
    "meeting-refreshment-catering-tainan": {
        "budget_range": "8,000–90,000",
        "person_range": "15–300 人",
        "hero_hook": "會議茶點要準時、好拿、好分發，讓會議節奏不被打斷。",
        "ad_angle": "企業會議、研討會、校園講座的高效率餐點",
        "cta_line": "先傳人數與會議時段，我們幫你評估茶點、午餐盒與飲品配置。",
        "faq_extra": [
            ("會議茶點需要先準備桌次嗎？", "看場地與出餐形式決定，通常會先確認桌數與上菜動線。"),
            ("如果是學校或研討會可以開發票嗎？", "可以，會以正式報價與出餐流程配合窗口作業。"),
        ],
        "internal_links": ["catering-corporate-tainan", "school-event-catering-tainan", "brand-event-catering"],
    },
    "brand-event-catering": {
        "budget_range": "12,000–70,000",
        "person_range": "20–120 人",
        "hero_hook": "品牌活動、賞車、建案發表，需要的是體面、畫面與停留感。",
        "ad_angle": "賞車、建案、展覽開幕、VIP 接待的場景感",
        "cta_line": "先傳品牌主題與活動照片，我們幫你對齊餐桌風格與視覺。",
        "faq_extra": [
            ("品牌活動可以做客製色系嗎？", "可以，會依主視覺與現場佈置做餐檯整合。"),
            ("賞車或建案發表適合怎樣的餐點？", "通常會用方便取用又有畫面的茶點、甜點與飲品組合。"),
        ],
        "internal_links": ["opening-event-catering-tainan", "catering-corporate-tainan", "meeting-refreshment-catering-tainan"],
    },
    "catering-corporate-tainan": {
        "budget_range": "15,000–100,000",
        "person_range": "20–200 人",
        "hero_hook": "企業外燴要能處理會議、春酒、茶會與辦公室活動的實際流程。",
        "ad_angle": "公司茶會、企業活動、春酒與辦公室外燴",
        "cta_line": "先傳活動類型、時段與場地條件，我們回你可落地的方案。",
        "faq_extra": [
            ("企業外燴可以做到什麼程度？", "可從會議茶點到公司茶會、品牌接待與春酒整合規劃。"),
            ("需要現場服務人員嗎？", "視活動規模決定，會議與接待型活動通常建議搭配現場服務。"),
        ],
        "internal_links": ["meeting-refreshment-catering-tainan", "opening-event-catering-tainan", "brand-event-catering"],
    },
    "school-event-catering-tainan": {
        "budget_range": "10,000–80,000",
        "person_range": "30–400 人",
        "hero_hook": "校園活動看重穩定、整潔與分發效率，流程要先想好。",
        "ad_angle": "成大、南臺、長榮、崑山等校園活動與講座",
        "cta_line": "先傳場地、桌數與時間，我們幫你對齊校方流程。",
        "faq_extra": [
            ("校園活動可以做大量分發嗎？", "可以，會依入場與離場節奏規劃出餐方式。"),
            ("講座或畢典適合哪種餐點？", "多半以好拿、不易弄髒、能快速分送的茶點組合為主。"),
        ],
        "internal_links": ["meeting-refreshment-catering-tainan", "catering-corporate-tainan", "opening-event-catering-tainan"],
    },
    "catering-birthday-party-tainan": {
        "budget_range": "12,000–45,000",
        "person_range": "15–40 人",
        "hero_hook": "週歲、抓周、生日，不只是餐點，是整場家人的情緒與畫面。",
        "ad_angle": "週歲、抓周、生日、家庭聚會的溫度感",
        "cta_line": "先傳小朋友年紀、人數與場地，我們先幫你看動線。",
        "faq_extra": [
            ("抓周與生日可以一起規劃嗎？", "可以，會把儀式、拍照與用餐節奏一起排好。"),
            ("家庭聚會適合什麼形式？", "通常會看室內外空間與長輩、小孩動線，安排方便取用的餐點。"),
        ],
        "internal_links": ["catering-wedding-tainan", "religious-event-catering-tainan", "opening-event-catering-tainan"],
    },
    "catering-wedding-tainan": {
        "budget_range": "20,000–150,000",
        "person_range": "30–200 人",
        "hero_hook": "婚禮外燴要同時顧到畫面、動線和賓客的停留感受。",
        "ad_angle": "婚禮、證婚、迎賓茶點、Candy Bar 的整合場景",
        "cta_line": "先傳場地與儀式流程，我們幫你對齊迎賓茶點與動線。",
        "faq_extra": [
            ("戶外婚禮遇雨怎麼辦？", "會先規劃雨備動線與替代配置，避免流程卡住。"),
            ("迎賓茶點要怎麼和婚禮主流程搭配？", "會依賓客入場與拍照節奏調整餐點與擺放位置。"),
        ],
        "internal_links": ["catering-birthday-party-tainan", "opening-event-catering-tainan", "brand-event-catering"],
    },
    "religious-event-catering-tainan": {
        "budget_range": "10,000–50,000",
        "person_range": "20–120 人",
        "hero_hook": "神明安座、感恩茶會、廟宇儀式，需要的是莊重與流程穩定。",
        "ad_angle": "神明安座、感恩茶會、廟宇儀式的穩定出餐",
        "cta_line": "先傳儀式時段與人數，我們幫你把餐點節奏排好。",
        "faq_extra": [
            ("宗教儀式可以做低調莊重的配置嗎？", "可以，會以不干擾儀式的方式安排餐點與動線。"),
            ("適合多少人以上規劃外燴？", "從小型茶會到多桌儀式都可依實際需求調整。"),
        ],
        "internal_links": ["catering-birthday-party-tainan", "opening-event-catering-tainan", "catering-corporate-tainan"],
    },
}

SCENE_GALLERY_MAP = {
    "meeting-refreshment-catering-tainan": [
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250424_103320.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250424_103325.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250424_103343.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250424_103354.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250424_103401.jpg",
    ],
    "opening-event-catering-tainan": [
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250626_083630.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250626_083635.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250626_083636.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250626_125719.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250626_141346.jpg",
    ],
    "brand-event-catering": [
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250326_185850.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250326_185858.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250326_185904.jpg",
        Path.home() / "Desktop" / "wordpress 素材庫" / "contact-sheets" / "brand_img_0347.jpg",
        Path.home() / "Desktop" / "wordpress 素材庫" / "contact-sheets" / "brand_assets.jpg",
    ],
    "catering-corporate-tainan": [
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250503_112152.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250503_112159.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250503_112208.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250503_112222.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250503_112341.jpg",
    ],
    "school-event-catering-tainan": [
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250320_091049.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250320_091058.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250320_093550.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250320_094153.jpg",
        Path.home() / "Library" / "CloudStorage" / "GoogleDrive-pagewu1010@gmail.com" / "我的雲端硬碟" / "Takeout_extracted" / "Takeout" / "Google 相簿" / "2025 年的相片" / "IMG_20250320_094937.jpg",
    ],
}

SCENE_GALLERY_NOTES = {
    "meeting-refreshment-catering-tainan": [
        "會議茶點｜餐桌全景",
        "會議茶點｜桌面近拍",
        "會議茶點｜出餐動線",
        "會議茶點｜補餐節奏",
        "會議茶點｜場地整體感",
    ],
    "opening-event-catering-tainan": [
        "開幕茶會｜迎賓桌",
        "開幕茶會｜品牌視覺",
        "開幕茶會｜餐點擺設",
        "開幕茶會｜接待動線",
        "開幕茶會｜現場氛圍",
    ],
    "brand-event-catering": [
        "品牌活動｜VIP lounge",
        "品牌活動｜座位區",
        "品牌活動｜吧台 / 飲品",
        "品牌活動｜花藝與接待",
        "品牌活動｜場域氛圍",
    ],
    "catering-corporate-tainan": [
        "企業外燴｜會議 / 茶會桌",
        "企業外燴｜接待配置",
        "企業外燴｜出餐動線",
        "企業外燴｜整體場域",
        "企業外燴｜活動節奏",
    ],
    "school-event-catering-tainan": [
        "校園活動｜講座茶點",
        "校園活動｜桌面配置",
        "校園活動｜分發動線",
        "校園活動｜活動現場",
        "校園活動｜整體氛圍",
    ],
}

PUBLISH_SIM_META = {
    "meeting-refreshment-catering-tainan": {
        "internal_date": "2025-04-24",
        "scene_compare": "會議茶點 / 研討會 / 校園講座",
        "seo_use": "meeting-refreshment-catering-tainan",
        "drive_hint": "Takeout_extracted / Google 相簿 / 2025 年的相片",
    },
    "opening-event-catering-tainan": {
        "internal_date": "2025-06-26",
        "scene_compare": "開幕茶會 / 診所 / 醫美 / 品牌開幕",
        "seo_use": "opening-event-catering-tainan",
        "drive_hint": "Takeout_extracted / Google 相簿 / 2025 年的相片",
    },
    "brand-event-catering": {
        "internal_date": "2025-03-26",
        "scene_compare": "品牌活動 / VIP 接待 / 車商 / 展覽開幕",
        "seo_use": "brand-event-catering",
        "drive_hint": "Takeout_extracted / Google 相簿 / 2025 年的相片",
    },
    "catering-corporate-tainan": {
        "internal_date": "2025-05-03",
        "scene_compare": "企業外燴 / 公司茶會 / 辦公室活動",
        "seo_use": "catering-corporate-tainan",
        "drive_hint": "Takeout_extracted / Google 相簿 / 2025 年的相片",
    },
    "school-event-catering-tainan": {
        "internal_date": "2025-03-20",
        "scene_compare": "校園活動 / 講座 / 畢典 / 研討會",
        "seo_use": "school-event-catering-tainan",
        "drive_hint": "Takeout_extracted / Google 相簿 / 2025 年的相片",
    },
}


def load_pages() -> list[dict]:
    data = json.loads(SCENARIO_JSON.read_text(encoding="utf-8"))
    return data["pages"]


def get_spec(page: dict) -> dict:
    base = {
        "budget_range": "請依活動規模報價",
        "person_range": "依現場人數調整",
        "hero_hook": f"{page['title']} 先把場景與節奏整理好，再進入菜單與流程。",
        "ad_angle": page["target_intent"],
        "cta_line": "先傳活動時段、人數、場地，我們幫你看適合的配置。",
        "faq_extra": [],
        "internal_links": [],
    }
    base.update(PAGE_SPEC.get(page["slug"], {}))
    return base


def get_scene_gallery(page: dict) -> list[Path]:
    gallery = SCENE_GALLERY_MAP.get(page["slug"])
    if not gallery:
        raise KeyError(f"missing gallery for {page['slug']}")
    return gallery


def get_scene_notes(page: dict) -> list[str]:
    return SCENE_GALLERY_NOTES.get(
        page["slug"],
        [f"{page['title']}｜素材 {i}/5" for i in range(1, 6)],
    )


def list_assets(folder: Path, suffixes: tuple[str, ...]) -> list[Path]:
    return sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in suffixes],
        key=lambda p: p.name.lower(),
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_asset(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def make_preview_image(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in {".heic", ".heif"}:
        subprocess.run(["sips", "-s", "format", "jpeg", str(src), "--out", str(dst)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    try:
        from PIL import Image

        with Image.open(src) as im:
            rgb = im.convert("RGB")
            rgb.save(dst, format="JPEG", quality=92, optimize=True)
        return
    except Exception:
        shutil.copy2(src, dst)


def render_faq_items(page: dict, spec: dict) -> list[tuple[str, str]]:
    common = [
        ("最早需要多久前預約？", "建議至少提前 2–4 週預約，熱門檔期請更早確認。"),
        ("可以客製菜單嗎？", "可以，會依活動人數、情境與現場條件做客製化提案。"),
        ("服務區域只有台南嗎？", "主要服務台南與周邊，跨區可依場次規模另行評估。"),
    ]
    return common + spec["faq_extra"]


def render_scene_gallery_block(page: dict, gallery_assets: list[Path]) -> str:
    notes = get_scene_notes(page)
    tiles = []
    for idx, asset in enumerate(gallery_assets):
        note = notes[idx] if idx < len(notes) else f"{page['title']}｜素材 {idx + 1}/5"
        tiles.append(
            f"""
            <figure>
              <img src="preview-assets/gallery-{idx + 1}.jpg" alt="{html.escape(note)}">
              <figcaption>{html.escape(note)}<br><span class="muted">{html.escape(asset.name)}</span></figcaption>
            </figure>
            """
        )
    return "\n".join(tiles)


def render_wp_draft(page: dict, spec: dict, scene_gallery: list[Path]) -> str:
    faq_md = "\n".join(
        f"- **{q}**：{a}" for q, a in render_faq_items(page, spec)
    )
    internal_links = "\n".join(f"- {item}" for item in spec["internal_links"])
    source_cases = "\n".join(f"- {case}" for case in page["source_cases"])
    gallery_md = "\n".join(
        f"- Gallery {i + 1}: <相片 {asset.name}>"
        for i, asset in enumerate(scene_gallery)
    )
    return f"""# {page['title']}

{spec['hero_hook']}

## 這一頁要解的搜尋意圖

{page['target_intent']}

## 適合的活動類型

- {page['target_intent']}
- 以 {page['key_keyword']} 為主軸的高意圖詢問
- 需要餐點、動線與場景一起規劃的活動

## 適合人數

{spec['person_range']}

## 規劃方式

依活動規模、場地條件與接待節奏規劃，不在公開頁面列固定價格。

## 真實案例

{source_cases}

## 服務重點

1. 先看活動場景，再決定菜單與擺設。
2. 先對齊人數與時間，再估算出餐與人力。
3. 先確定 CTA 與詢問路徑，再談素材與內連。

## FAQ

{faq_md}

## LINE CTA

{spec['cta_line']}

## 內部連結

{internal_links}

## 圖片插槽

- 圖片組：
{gallery_md}

## Rank Math 寫入重點

- Focus keyword: {page['key_keyword']}
- Title: {page['title']}｜MAPLAB Kitchen
- Description: MAPLAB Kitchen 提供 {page['target_intent']} 的外燴與活動餐點規劃。
- Schema: Service + FAQPage + FoodService
"""


def render_ad_copy(page: dict, spec: dict, scene_gallery: list[Path]) -> str:
    headlines = [
        f"{page['title']}｜{page['key_keyword']}",
        f"{page['title']}｜{spec['ad_angle']}",
        f"MAPLAB Kitchen｜{page['title']}",
    ]
    primary_a = f"這是一份給 {page['target_intent']} 的素材包。先看畫面與節奏，再安排人數、現場動線與接待配置。"
    primary_b = f"{spec['hero_hook']} 如果你正在找 {page['key_keyword']}，先把活動時段、人數與場地條件傳來，我們直接對齊可用方案。"
    image_slots = "\n".join(
        f"- Scene {i + 1}: <相片 {asset.name}>"
        for i, asset in enumerate(scene_gallery)
    )
    return f"""# {page['title']} — Ad Copy

Headline options:
1. {headlines[0]}
2. {headlines[1]}
3. {headlines[2]}

Primary text A:
{primary_a}

Primary text B:
{primary_b}

Image slots:
{image_slots}

CTA:
先傳活動時段、人數、場地，我們再幫你對齊方案。
"""


def render_tracking_note(page: dict, spec: dict) -> str:
    return f"""# Tracking Notes — {page['title']}

- Campaign slug: {page['slug']}
- Page slug: {page['slug']}
- Target keyword: {page['key_keyword']}
- Budget range: {spec['budget_range']}
- Person range: {spec['person_range']}
- Source cases: {", ".join(page['source_cases'])}
- Review state: draft_only
"""


def render_rankmath_payload(page: dict, spec: dict) -> dict:
    return {
        "slug": page["slug"],
        "title": page["title"],
        "status": "draft",
        "rank_math_focus_keyword": page["key_keyword"],
        "rank_math_title": f"{page['title']}｜MAPLAB Kitchen",
        "rank_math_description": f"MAPLAB Kitchen 提供 {page['target_intent']} 的外燴與活動餐點規劃。",
        "schema": ["Service", "FAQPage", "FoodService"],
        "source_cases": page["source_cases"],
        "internal_links": spec["internal_links"],
    }


def render_preview_html(page: dict, spec: dict, scene_gallery: list[Path]) -> str:
    faq_items = render_faq_items(page, spec)
    faq_html = "\n".join(
        f"<li><strong>{html.escape(q)}</strong><br>{html.escape(a)}</li>" for q, a in faq_items
    )
    case_html = "\n".join(f"<li>{html.escape(case)}</li>" for case in page["source_cases"])
    internal_html = "\n".join(f"<li>{html.escape(item)}</li>" for item in spec["internal_links"])
    gallery_html = render_scene_gallery_block(page, scene_gallery)
    photo_notes = "\n".join(
        f"<li>{html.escape(notes)}</li>" for notes in get_scene_notes(page)
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page['title'])}｜Preview</title>
  <style>
    :root {{
      --bg: #faf7f2;
      --card: #ffffff;
      --line: #e5ddd1;
      --text: #1f2937;
      --muted: #6b7280;
      --accent: #8b5e3c;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      background: var(--bg);
      color: var(--text);
    }}
    .wrap {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      margin-bottom: 20px;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: #f3efe7;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 18px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}
    h1,h2,h3 {{ margin: 0 0 10px; }}
    h1 {{ font-size: 32px; }}
    h2 {{ font-size: 20px; margin-top: 0; }}
    p {{ line-height: 1.65; margin: 0 0 12px; }}
    ul,ol {{ margin: 0 0 12px 22px; }}
    .gallery {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      align-items: start;
    }}
    figure {{
      margin: 0;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fff;
    }}
    img {{
      width: 100%;
      height: 210px;
      object-fit: contain;
      background: linear-gradient(180deg, #1f2937, #111827);
      border-radius: 8px;
    }}
    figcaption {{
      margin-top: 8px;
      font-size: 13px;
      color: var(--muted);
    }}
    .muted {{ color: var(--muted); }}
    .section + .section {{ margin-top: 14px; }}
    @media (max-width: 900px) {{
      .grid, .gallery {{ grid-template-columns: 1fr; }}
      img {{ height: 260px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <div class="badge">WordPress Preview</div>
        <h1>{html.escape(page['title'])}</h1>
        <p class="muted">{html.escape(page['key_keyword'])} · {html.escape(spec['person_range'])} · public draft</p>
      </div>
      <div class="badge">draft / review only</div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="gallery">
          {gallery_html}
        </div>
      </div>

      <div class="card">
        <h2>頁面摘要</h2>
        <p>{html.escape(spec['hero_hook'])}</p>
        <p><strong>目標意圖：</strong>{html.escape(page['target_intent'])}</p>
        <p><strong>真實案例：</strong></p>
        <ul>{case_html}</ul>
        <p><strong>照片說明：</strong></p>
        <ul>{photo_notes}</ul>
        <p><strong>內部連結：</strong></p>
        <ul>{internal_html}</ul>
      </div>
    </div>

    <div class="grid" style="margin-top:18px;">
      <div class="card section">
        <h2>草稿內容</h2>
        <div style="white-space: pre-wrap;">{html.escape(render_wp_draft(page, spec, scene_gallery))}</div>
      </div>

      <div class="card section">
        <h2>Rank Math / SEO</h2>
        <ul>
          <li><strong>Focus keyword:</strong> {html.escape(page['key_keyword'])}</li>
          <li><strong>Title:</strong> {html.escape(page['title'])}｜MAPLAB Kitchen</li>
          <li><strong>Description:</strong> MAPLAB Kitchen 提供 {html.escape(page['target_intent'])} 的外燴與活動餐點規劃。</li>
          <li><strong>Schema:</strong> Service + FAQPage + FoodService</li>
        </ul>
        <h3>FAQ</h3>
        <ul>{faq_html}</ul>
        <h3>CTA</h3>
        <p>{html.escape(spec['cta_line'])}</p>
      </div>
    </div>
  </div>
</body>
</html>
"""


def render_ads_preview_html(page: dict, spec: dict, scene_gallery: list[Path]) -> str:
    gallery_html = render_scene_gallery_block(page, scene_gallery)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page['title'])}｜Ad Preview</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #0f172a; color: #e5e7eb; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
    .card {{ background: #111827; border: 1px solid #334155; border-radius: 12px; padding: 18px; margin-bottom: 16px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .gallery {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
    img {{ width: 100%; height: 180px; object-fit: contain; background: #1f2937; border-radius: 10px; }}
    h1,h2,h3,p,ul {{ margin-top: 0; }}
    .muted {{ color: #94a3b8; }}
    figcaption {{ color: #94a3b8; font-size: 12px; margin-top: 6px; line-height: 1.45; }}
    figure {{ margin: 0; }}
    @media (max-width: 900px) {{ .grid, .gallery {{ grid-template-columns: 1fr; }} img {{ height: 240px; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>{html.escape(page['title'])}｜Ad Preview</h1>
      <p class="muted">{html.escape(page['key_keyword'])} · {html.escape(spec['ad_angle'])}</p>
    </div>
    <div class="grid">
      <div class="card">
        <div class="gallery">
          {gallery_html}
        </div>
      </div>
      <div class="card">
        <h2>素材說明</h2>
        <p class="muted">{html.escape(page['key_keyword'])} · {html.escape(spec['ad_angle'])}</p>
        <ul>
          <li>先看 5 張場景照，再看文案與 TA。</li>
          <li>圖片與標題要回到同一個活動場景。</li>
          <li>不直接發布，只產 draft / review。</li>
        </ul>
      </div>
    </div>
    <div class="card">
      <h2>文案</h2>
      <pre style="white-space: pre-wrap; margin:0;">{html.escape(render_ad_copy(page, spec, scene_gallery))}</pre>
    </div>
  </div>
</body>
</html>
"""


def make_command_text(path: Path, body: str) -> None:
    write_text(path, body)
    os.chmod(path, 0o755)


def render_openclaw_prompt(page: dict, spec: dict, task_dir: Path, kind: str) -> str:
    if kind == "wordpress":
        return dedent(
            f"""\
            你是 MAPLAB A2 WordPress 草稿 worker。

            work_package: {task_dir}
            task_kind: wordpress
            goal: 先檢查圖文與 Rank Math，輸出 draft/review，不直接發布。

            你必讀：
            - brief.md
            - draft.md
            - seo.md
            - outline.md
            - internal_links.md
            - rankmath_payload.json
            - source_bridge.md
            - preview.html

            你要做的事：
            1. 檢查 preview.html 的圖文與圖片插槽是否合理。
            2. 檢查 draft.md 是否符合 H1 / FAQ / CTA / 內連結 / 場景與人數；draft.md 是 public-safe，不得寫價格、內部日期或 file:// 本機路徑。
            3. 必要時微調 draft.md 與 rankmath_payload.json。
            4. 在 review 區寫回 task_request.md、execution_log.json、review_request.md。

            限制：
            - 不要發布 WordPress
            - 不要推 main
            - 不要改原始素材
            - 只產 draft / review bundle
            """
        ).strip()

    return dedent(
        f"""\
        你是 MAPLAB A3 廣告 worker。

        work_package: {task_dir}
        task_kind: ads
        goal: 先檢查素材、文案與 TA，輸出 draft/review，不直接發布。

        你必讀：
        - brief.md
        - copy.md
        - ta.md
        - asset_map.md
        - source_bridge.md
        - preview.html

        你要做的事：
        1. 檢查 preview.html 的圖文是否合理。
        2. 檢查 copy.md 的標題、主文、CTA 是否符合場景。
        3. 必要時微調 copy.md、ta.md、asset_map.md。
        4. 在 review 區寫回 task_request.md、execution_log.json、review_request.md。

        限制：
        - 不要發布廣告
        - 不要推 main
        - 不要改原始素材
        - 只產 draft / review bundle
        """
    ).strip()


def render_run_command(task_dir: Path, prompt_filename: str, job_prefix: str, model: str = "qwen2.5-coder:7b") -> str:
    task_dir_literal = shell_quote(str(task_dir))
    model_literal = json.dumps(model)
    return dedent(
        f"""\
        #!/bin/zsh
        set -euo pipefail

        TASK_DIR={task_dir_literal}
        PROMPT_FILE="$TASK_DIR/{prompt_filename}"
        JOB_ID="{job_prefix}-$(date +%Y%m%d-%H%M%S)"
        RUN_DIR="$TASK_DIR/review/$JOB_ID"

        mkdir -p "$RUN_DIR"
        cp "$PROMPT_FILE" "$RUN_DIR/task_request.md"

        openclaw agent --local \
          --session-id "$JOB_ID" \
          --model {model_literal} \
          --thinking minimal \
          --message "$(cat "$PROMPT_FILE")" \
          --json | tee "$RUN_DIR/openclaw.json"
        """
    ).strip() + "\n"


def render_schedule_command(task_dir: Path, prompt_filename: str, cron_name: str, model: str = "qwen2.5-coder:7b") -> str:
    task_dir_literal = shell_quote(str(task_dir))
    model_literal = json.dumps(model)
    cron_name_literal = json.dumps(cron_name)
    return dedent(
        f"""\
        #!/bin/zsh
        set -euo pipefail

        TASK_DIR={task_dir_literal}
        PROMPT_FILE="$TASK_DIR/{prompt_filename}"
        JOB_ID="{cron_name}-$(date +%Y%m%d-%H%M%S)"
        RUN_DIR="$TASK_DIR/review/$JOB_ID"
        RUN_AT="$(python3 - <<'PY'
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

tz = ZoneInfo("Asia/Taipei")
now = datetime.now(tz)
target = now.replace(hour=2, minute=0, second=0, microsecond=0)
if now >= target:
    target += timedelta(days=1)
print(target.isoformat())
PY
)"

        mkdir -p "$RUN_DIR"
        cp "$PROMPT_FILE" "$RUN_DIR/task_request.md"

        openclaw cron add \
          --name {cron_name_literal} \
          --at "$RUN_AT" \
          --delete-after-run \
          --expect-final \
          --light-context \
          --session isolated \
          --model {model_literal} \
          --thinking minimal \
          --message "$(cat "$PROMPT_FILE")" \
          --json | tee "$RUN_DIR/cron.json"
        """
    ).strip() + "\n"


def file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def shell_quote(text: str) -> str:
    return "'" + text.replace("'", "'\"'\"'") + "'"


def collect_broken_links(html_paths: list[Path]) -> list[tuple[Path, str, str, Path]]:
    broken: list[tuple[Path, str, str, Path]] = []
    skip = re.compile(r"^(https?:|#|mailto:|javascript:|data:)")

    for html_path in html_paths:
        if not html_path.exists():
            broken.append((html_path, "file", str(html_path), html_path))
            continue
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        for attr in ("href", "src"):
            for match in re.finditer(rf"{attr}=[\"']([^\"']+)[\"']", text):
                target = match.group(1)
                if skip.match(target):
                    continue
                if target.startswith("file://"):
                    parsed_path = Path(unquote(urlparse(target).path))
                else:
                    parsed_path = (html_path.parent / target).resolve()
                if not parsed_path.exists():
                    broken.append((html_path, attr, target, parsed_path))
    return broken


def verify_html_links(html_paths: list[Path]) -> None:
    broken = collect_broken_links(html_paths)
    if broken:
        details = "\n".join(
            f"- {html_path}: {attr}={target} -> {resolved}"
            for html_path, attr, target, resolved in broken
        )
        raise RuntimeError(f"broken links found:\n{details}")


def verify_public_outputs(public_paths: list[Path]) -> None:
    price_pattern = re.compile(r"\d{1,3},\d{3}(?:[–-]\d{1,3},\d{3})?")
    forbidden_labels = ("file://", "日期（內部", "Google Drive 動態連結")
    failures: list[str] = []

    for path in public_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if price_pattern.search(text):
            failures.append(f"{path}: contains public price range")
        for label in forbidden_labels:
            if label in text:
                failures.append(f"{path}: contains {label}")

    if failures:
        raise RuntimeError("public output safety check failed:\n" + "\n".join(f"- {item}" for item in failures))


def render_handoff_board_html(pages: list[dict], workbench_dir: Path, preview_root: Path, jobs_dir: Path, openclaw_dashboard_cmd: Path) -> str:
    shortcut_dir = Path.home() / "Desktop" / "MAPLAB_A2A3_Workbench"

    def task_cards(kind: str) -> str:
        cards = []
        for page in pages:
            task_dir = workbench_dir / kind / page["slug"]
            prompt_id = f"{kind}-{page['slug']}"
            prompt_text = render_openclaw_prompt(page, get_spec(page), task_dir, kind)
            preview_path = task_dir / "preview.html"
            command_kind = "wp" if kind == "wordpress" else kind
            run_cmd = jobs_dir / f"run_{command_kind}_{page['slug']}.command"
            schedule_cmd = jobs_dir / f"schedule_{command_kind}_{page['slug']}.command"
            cards.append(
                f"""
                <article class="task-card" data-search="{html.escape(page['title'] + ' ' + page['slug'] + ' ' + page['target_intent'] + ' ' + ' '.join(page['source_cases']))}">
                  <div class="task-head">
                    <div>
                      <div class="eyebrow">{'WordPress 草稿包' if kind == 'wordpress' else '廣告素材包'}</div>
                      <h3>{html.escape(page['title'])}</h3>
                      <p class="muted">{html.escape(page['target_intent'])}</p>
                    </div>
                    <span class="pill">{html.escape(page['key_keyword'])}</span>
                  </div>
                  <div class="meta">
                    <span>來源：{html.escape(', '.join(page['source_cases']))}</span>
                    <span>人數：{html.escape(get_spec(page)['person_range'])}</span>
                    <span>預算：{html.escape(get_spec(page)['budget_range'])}</span>
                  </div>
                  <div class="task-grid">
                    <div class="mini-card">
                      <h4>OpenClaw 工作包</h4>
                      <p class="muted">只讀這個資料夾，不看整個 Drive。</p>
                      <div class="actions">
                        <a href="{file_uri(task_dir)}">開資料夾</a>
                        <a href="{file_uri(preview_path)}">開預覽</a>
                        <a href="{file_uri(run_cmd)}">Run now</a>
                        <a href="{file_uri(schedule_cmd)}">Tonight</a>
                        <button data-copy="{prompt_id}" onclick="copyPrompt('{prompt_id}')">Copy prompt</button>
                      </div>
                    </div>
                    <div class="mini-card">
                      <h4>{'WordPress / Rank Math' if kind == 'wordpress' else 'Ad Copy / TA'}</h4>
                      <p class="muted">{'draft.md public-safe + rankmath_payload.json + source_bridge.md internal' if kind == 'wordpress' else 'copy.md + ta.md + asset_map.md + source_bridge.md'}</p>
                      <textarea id="{prompt_id}" readonly>{html.escape(prompt_text)}</textarea>
                    </div>
                  </div>
                </article>
                """
            )
        return "\n".join(cards)

    wp_cards = task_cards("wordpress")
    ad_cards = task_cards("ads")

    batch_prompt = render_nightly_batch_prompt(pages, workbench_dir)
    batch_prompt_path = jobs_dir / "nightly_batch_prompt.md"
    write_text(batch_prompt_path, batch_prompt)

    board = f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MAPLAB A2/A3 Handoff Board</title>
  <style>
    :root {{
      --bg: #f6f1e8;
      --card: #ffffff;
      --line: #e5ddd1;
      --text: #1f2937;
      --muted: #6b7280;
      --accent: #8b5e3c;
      --accent-2: #2f6f5e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
    .hero {{
      background: linear-gradient(135deg, #fff, #f8f2e8);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      margin-bottom: 18px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.03);
    }}
    .hero-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}
    h1 {{ margin: 0 0 8px; font-size: 32px; }}
    .muted {{ color: var(--muted); }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }}
    .toolbar a, .toolbar button, .task-card a, .task-card button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line);
      background: #fff;
      color: var(--text);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 14px;
      text-decoration: none;
      cursor: pointer;
    }}
    .toolbar a:hover, .toolbar button:hover, .task-card a:hover, .task-card button:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 16px;
    }}
    .stat {{
      background: rgba(255,255,255,0.8);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }}
    .stat .num {{ display:block; font-size: 28px; font-weight: 700; color: var(--accent); }}
    .section {{ margin-top: 24px; }}
    .section-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: end;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}
    .section-head input {{
      min-width: 240px;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 14px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 16px;
    }}
    .task-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .task-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }}
    .task-head h3 {{ margin: 2px 0 4px; font-size: 22px; }}
    .eyebrow {{
      display: inline-block;
      font-size: 12px;
      letter-spacing: .02em;
      text-transform: uppercase;
      color: var(--accent-2);
      font-weight: 700;
    }}
    .pill {{
      white-space: nowrap;
      padding: 4px 10px;
      background: #f3efe7;
      color: var(--accent);
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 12px;
      font-size: 13px;
      color: var(--muted);
      margin: 10px 0 14px;
    }}
    .task-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .mini-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      background: #fff;
    }}
    .mini-card h4 {{ margin: 0 0 8px; font-size: 16px; }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }}
    textarea {{
      width: 100%;
      min-height: 212px;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      line-height: 1.55;
      resize: vertical;
      background: #fcfbf8;
    }}
    .batch {{
      background: linear-gradient(135deg, #fff, #f7fbf8);
      border-color: #cde5d8;
    }}
    .batch pre {{
      white-space: pre-wrap;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      font-size: 12px;
      overflow: auto;
    }}
    @media (max-width: 1000px) {{
      .stats, .task-grid {{ grid-template-columns: 1fr; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="hero-top">
        <div>
          <div class="eyebrow">MAPLAB A2/A3 Handoff Board</div>
          <h1>點任務就能交辦，按鈕直接進 OpenClaw</h1>
          <p class="muted">這不是另一份漂亮文件，而是你今天真的會用的交接面板：看圖文、開資料夾、複製 prompt、直接跑 OpenClaw，或排到夜間 batch。</p>
        </div>
        <div class="pill">draft / review only</div>
      </div>

      <div class="toolbar">
        <a href="{file_uri(workbench_dir / 'README.md')}">A2/A3 Workbench README</a>
        <a href="{file_uri(shortcut_dir / '00_open_launchpad.command')}">Open Launchpad</a>
        <a href="{file_uri(openclaw_dashboard_cmd)}">OpenClaw Dashboard</a>
        <a href="{file_uri(preview_root)}">WordPress Preview Root</a>
        <a href="{file_uri(shortcut_dir / '04_open_wordpress_materials.command')}">Open WordPress Materials</a>
        <a href="{file_uri(shortcut_dir / '05_open_wordpress_preview.command')}">Open WordPress Preview</a>
        <a href="{file_uri(jobs_dir / 'schedule_nightly_batch.command')}">Schedule Night Batch</a>
      </div>
      <div style="margin-top: 14px;">
        <input type="search" placeholder="搜尋關鍵字、slug、案例（例如：開幕 / 週歲 / 賓士）" style="width: min(100%, 520px); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; font-size: 14px;">
      </div>

      <div class="stats">
        <div class="stat"><span class="num">{len(pages)}</span><span class="muted">工作包對</span></div>
        <div class="stat"><span class="num">{len(pages) * 2}</span><span class="muted">WordPress / Ads 資料夾</span></div>
        <div class="stat"><span class="num">1</span><span class="muted">夜間排程命令</span></div>
        <div class="stat"><span class="num">2</span><span class="muted">可直接執行的模式</span></div>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>夜間批次</h2>
          <p class="muted">先把所有資料夾丟進 OpenClaw，再用 cron 排到睡覺時跑。適合做整批草稿 / 素材整合 / tracking 對齊。</p>
        </div>
      </div>
      <div class="task-card batch">
        <div class="task-head">
          <div>
            <div class="eyebrow">Batch / Schedule</div>
            <h3>MAPLAB A2/A3 Night Batch</h3>
            <p class="muted">如果你今晚不碰電腦，直接按這個排程。它會讀 `jobs/nightly_batch_prompt.md`，把 8 個 WordPress + 8 個 Ads 包一次排進 OpenClaw cron。</p>
          </div>
          <span class="pill">schedule 02:00 Taipei</span>
        </div>
        <div class="actions">
          <a href="{file_uri(jobs_dir / 'schedule_nightly_batch.command')}">Schedule tonight</a>
          <a href="{file_uri(jobs_dir / 'run_nightly_batch.command')}">Run batch now</a>
          <button onclick="copyPrompt('nightly-batch')">Copy batch prompt</button>
        </div>
        <textarea id="nightly-batch" readonly>{html.escape(batch_prompt)}</textarea>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>WordPress 工作包</h2>
          <p class="muted">每個卡片代表一篇文章：先看預覽，再決定要不要跑 OpenClaw。</p>
        </div>
      </div>
      <div class="grid">{wp_cards}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>廣告素材包</h2>
          <p class="muted">每個卡片對應同一個場景的廣告 copy / TA / asset map。可以直接交給 OpenClaw 產草稿。</p>
        </div>
      </div>
      <div class="grid">{ad_cards}</div>
    </section>
  </div>

  <script>
    function copyPrompt(id) {{
      const el = document.getElementById(id);
      if (!el) return;
      navigator.clipboard.writeText(el.value).then(() => {{
        const prev = document.title;
        document.title = '已複製 ' + id;
        window.setTimeout(() => document.title = prev, 1200);
      }});
    }}

    const search = document.querySelector('input[type="search"]');
    if (search) {{
      search.addEventListener('input', () => {{
        const value = search.value.trim().toLowerCase();
        document.querySelectorAll('.task-card[data-search]').forEach((card) => {{
          const hay = card.getAttribute('data-search') || '';
          card.style.display = hay.toLowerCase().includes(value) ? '' : 'none';
        }});
      }});
    }}
  </script>
</body>
</html>
"""
    return board


def render_publish_sim_html(pages: list[dict]) -> str:
    sections = []
    for page in pages:
        spec = get_spec(page)
        gallery = get_scene_gallery(page)
        notes = get_scene_notes(page)
        meta = PUBLISH_SIM_META.get(page["slug"], {})
        gallery_bits = []
        for idx, asset in enumerate(gallery):
            note = notes[idx] if idx < len(notes) else f"{page['title']}｜素材 {idx + 1}/5"
            gallery_bits.append(
                f"""
                <figure>
                  <img src="wordpress/{page['slug']}/preview-assets/gallery-{idx + 1}.jpg" alt="{html.escape(note)}">
                  <figcaption>{html.escape(note)}<br><span class="muted">{html.escape(asset.name)}</span></figcaption>
                </figure>
                """
            )
        gallery_html = "\n".join(gallery_bits)
        photo_notes = "<br>".join(html.escape(note) for note in notes)
        drive_link = file_uri(gallery[0])
        sections.append(
            f"""
            <section class="case">
              <div class="media">
                <div class="gallery">
                  {gallery_html}
                </div>
                <div class="source-note">
                  <strong>{html.escape(page['title'])}</strong><br>
                  場景比較：{html.escape(meta.get('scene_compare', page['target_intent']))}<br>
                  SEO 用途：{html.escape(meta.get('seo_use', page['slug']))}<br>
                  日期（內部核對）：{html.escape(meta.get('internal_date', 'internal only'))}<br>
                  Google Drive：<a href="{drive_link}">{html.escape(meta.get('drive_hint', gallery[0].name))}</a>
                </div>
              </div>
              <div class="content">
                <div class="head">
                  <p class="eyebrow">Scene {html.escape(page['slug'])}</p>
                  <div class="title-row">
                    <div>
                      <h2>{html.escape(page['title'])}</h2>
                      <p class="slug">{html.escape(page['key_keyword'])} · {html.escape(spec['person_range'])} · internal QA</p>
                    </div>
                    <a class="preview-link" href="wordpress/{page['slug']}/preview.html">Open preview</a>
                  </div>
                </div>
                <p class="lead">{html.escape(spec['hero_hook'])}</p>
                <table class="matrix">
                  <tr><th>場景比較資料</th><td>{html.escape(meta.get('scene_compare', page['target_intent']))}</td></tr>
                  <tr><th>SEO 給哪個場景用的素材</th><td>{html.escape(meta.get('seo_use', page['slug']))}</td></tr>
                  <tr><th>日期</th><td>{html.escape(meta.get('internal_date', 'internal only'))}</td></tr>
                  <tr><th>Google Drive 動態連結</th><td><a href="{drive_link}">{html.escape(meta.get('drive_hint', gallery[0].name))}</a></td></tr>
                  <tr><th>照片敘述</th><td>{photo_notes}</td></tr>
                </table>
                <div class="footer-note">
                  真實案例：{html.escape(', '.join(page['source_cases']))}<br>
                  這裡只做核對與預覽，公開稿仍然去日期化。
                </div>
              </div>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MAPLAB B2B 模擬發布板</title>
  <style>
    :root {{
      --bg: #0f1115;
      --panel: #171b22;
      --panel2: #1d232d;
      --text: #eef2f7;
      --muted: #a8b2c3;
      --line: #2c3440;
      --accent: #e8b15d;
      --accent2: #8bd3ff;
      --good: #92d18b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: linear-gradient(180deg, #10141a, #0f1115);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: rgba(8,10,13,.75);
      position: sticky;
      top: 0;
      backdrop-filter: blur(8px);
      z-index: 3;
    }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .sub {{ margin: 0; color: var(--muted); max-width: 1020px; line-height: 1.65; }}
    .bar {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:14px; }}
    .chip {{
      border:1px solid var(--line);
      background: var(--panel);
      padding:8px 12px;
      border-radius:999px;
      color: var(--text);
      font-size: 13px;
    }}
    main {{ padding: 24px 32px 40px; }}
    .summary {{
      display:grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .summary .box {{
      background: var(--panel);
      border:1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }}
    .summary .box span {{
      display:block;
      color: var(--accent2);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .summary .box strong {{ font-size: 18px; }}
    .note {{
      margin: 0 0 20px;
      padding: 14px 16px;
      border: 1px solid rgba(139,211,255,.28);
      border-radius: 14px;
      background: rgba(19, 27, 37, .84);
      color: var(--muted);
      line-height: 1.7;
    }}
    .stack {{ display:grid; gap: 18px; }}
    .case {{
      display:grid;
      grid-template-columns: minmax(340px, 44%) minmax(0, 1fr);
      gap: 18px;
      background: rgba(23,27,34,.95);
      border:1px solid var(--line);
      border-radius: 18px;
      overflow:hidden;
      box-shadow: 0 16px 40px rgba(0,0,0,.18);
    }}
    .media {{
      padding: 18px;
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,0));
    }}
    .gallery {{
      display:grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .gallery figure {{ margin: 0; }}
    .gallery img {{
      width: 100%;
      height: 178px;
      object-fit: contain;
      background: linear-gradient(180deg, #1f2937, #111827);
      border-radius: 12px;
      border: 1px solid var(--line);
      display:block;
    }}
    .gallery figcaption {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }}
    .content {{ padding: 18px 18px 20px 0; }}
    .head {{ padding: 0 18px 14px 0; border-bottom: 1px solid var(--line); }}
    .eyebrow {{ margin:0 0 8px; text-transform:uppercase; letter-spacing:.08em; color: var(--accent2); font-size: 12px; }}
    .title-row {{ display:flex; justify-content:space-between; gap: 16px; align-items:flex-start; }}
    h2 {{ margin: 0 0 6px; font-size: 24px; }}
    .slug {{ margin:0; color: var(--muted); font-size: 13px; }}
    .preview-link {{
      display:inline-block;
      text-decoration:none;
      color:#111;
      background: var(--accent);
      padding:10px 14px;
      border-radius:10px;
      font-weight:700;
      white-space:nowrap;
    }}
    .lead {{
      margin: 14px 18px 14px 0;
      color: var(--text);
      line-height: 1.7;
      font-size: 15px;
    }}
    .matrix {{
      width: calc(100% - 18px);
      border-collapse: collapse;
      margin-right: 18px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--panel2);
    }}
    .matrix th,
    .matrix td {{
      text-align:left;
      vertical-align: top;
      padding: 14px 14px;
      border-bottom: 1px solid var(--line);
    }}
    .matrix tr:last-child th,
    .matrix tr:last-child td {{ border-bottom: none; }}
    .matrix th {{
      width: 188px;
      color: var(--accent2);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: .02em;
      background: rgba(255,255,255,.015);
    }}
    .matrix td {{
      color: var(--text);
      font-size: 14px;
      line-height: 1.65;
    }}
    .matrix ul {{
      margin: 0;
      padding-left: 20px;
      line-height: 1.8;
    }}
    .meta-inline {{
      display:flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 6px;
    }}
    .pill {{
      display:inline-flex;
      align-items:center;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(139,211,255,.12);
      color: #cdeaff;
      border: 1px solid rgba(139,211,255,.18);
      font-size: 12px;
    }}
    .link-list {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 8px;
    }}
    .link-list a {{
      color: #111;
      background: #e8b15d;
      display: inline-block;
      text-decoration: none;
      padding: 8px 12px;
      border-radius: 10px;
      font-weight: 700;
      margin-right: 8px;
      margin-bottom: 6px;
    }}
    .link-list .secondary {{
      background: transparent;
      color: var(--text);
      border: 1px solid var(--line);
      font-weight: 600;
    }}
    .small {{ color: var(--muted); font-size: 12px; }}
    .footer-note {{
      padding: 14px 18px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.6;
    }}
    a {{ color: #f2c97d; }}
    @media (max-width: 1100px) {{
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .case {{ grid-template-columns: 1fr; }}
      .media {{ border-right: none; border-bottom: 1px solid var(--line); }}
      .content {{ padding: 0 18px 20px 18px; }}
      .head, .lead, .matrix, .footer-note {{ width: 100%; margin-right: 0; }}
      .matrix th {{ width: 160px; }}
    }}
    @media (max-width: 760px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .summary {{ grid-template-columns: 1fr; }}
      .title-row {{ flex-direction: column; }}
      .preview-link {{ align-self: flex-start; }}
      .matrix th, .matrix td {{ display: block; width: 100%; }}
      .matrix th {{ padding-bottom: 4px; border-bottom: none; }}
      .matrix td {{ padding-top: 0; }}
      .gallery {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>MAPLAB B2B 模擬發布板</h1>
    <p class="sub">這一版把每個場景都補成 5 張真實照片，不再用單張 hero 或 IG 首頁 grid。左邊是場景畫廊，右邊是場景比較、SEO 用法、日期和 Google Drive 核對表。</p>
    <div class="bar">
      <span class="chip">左圖 = 5-photo scene gallery</span>
      <span class="chip">右表 = 場景 / SEO / 日期 / Drive</span>
      <span class="chip">公開稿去日期化</span>
      <span class="chip">IG / 報價單 / 照片日期在內部矩陣核對</span>
      <span class="chip">Preview only</span>
    </div>
  </header>
  <main>
    <section class="summary">
      <div class="box"><span>Pages</span><strong>{len(pages)}</strong></div>
      <div class="box"><span>Confirmed cases</span><strong>25+</strong></div>
      <div class="box"><span>Public draft dates</span><strong>0</strong></div>
      <div class="box"><span>Internal matrix</span><strong>5×5</strong></div>
      <div class="box"><span>Status</span><strong>Draft / Review</strong></div>
    </section>

    <p class="note">
      客觀檢查結果：現在的重點不是再補空泛主頁，而是把五個 B2B 場景各自補成 5 張真實照片的核對板。
      這樣你一眼就能看到 <strong>場景比較資料</strong>、<strong>SEO 用哪一組素材</strong>、<strong>日期（僅內部）</strong>、以及 <strong>Google Drive 動態連結</strong>。
    </p>

    <div class="stack">
      {''.join(sections)}
    </div>
  </main>
</body>
</html>
"""


def render_nightly_batch_prompt(pages: list[dict], workbench_dir: Path) -> str:
    lines = [
        "你是 MAPLAB A2/A3 夜間批次 worker。",
        f"workbench: {workbench_dir}",
        "goal: 依序處理所有 WordPress / Ads 工作包，只產 draft/review，不直接發布。",
        "",
        "執行順序：",
    ]
    for page in pages:
        lines.append(f"- WordPress: {workbench_dir / 'wordpress' / page['slug']}")
        lines.append(f"- Ads: {workbench_dir / 'ads' / page['slug']}")
    lines += [
        "",
        "規則：",
        "- 先讀每個資料夾的 brief.md / draft.md / preview.html",
        "- 只產 review bundle，不要推 main，不要發布 WordPress，不要投放廣告",
        "- 每個包完成後記錄 execution_log.json 與 review_request.md",
        "- 若遇到圖片裁切不合理，回報要修哪個 preview-assets，不要直接覆蓋原圖",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    pages = load_pages()
    scene_assets = list_assets(SOURCE_SCENE_DIR, (".heic", ".jpg", ".jpeg", ".png", ".webp"))
    food_assets = list_assets(SOURCE_FOOD_DIR, (".webp", ".jpg", ".jpeg", ".png"))

    missing_gallery_assets = [
        str(asset)
        for page in pages
        for asset in get_scene_gallery(page)
        if not asset.exists()
    ]
    if missing_gallery_assets:
        raise RuntimeError("scene gallery assets missing:\n" + "\n".join(f"- {asset}" for asset in missing_gallery_assets))
    if len(food_assets) < len(pages):
        raise RuntimeError(f"food assets not enough: {len(food_assets)} < {len(pages)}")

    DESKTOP_ROOT.mkdir(parents=True, exist_ok=True)
    ads_root = DESKTOP_ROOT / "ads"
    wp_root = DESKTOP_ROOT / "wordpress"
    tracking_root = DESKTOP_ROOT / "tracking"
    jobs_root = Path.home() / "Desktop" / "MAPLAB_A2A3_Workbench" / "jobs"
    for root in (ads_root, wp_root, tracking_root):
        root.mkdir(parents=True, exist_ok=True)
    jobs_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "source_sheet_url": SOURCE_SHEET_URL,
        "scene_source_dir": str(SOURCE_SCENE_DIR),
        "food_source_dir": str(SOURCE_FOOD_DIR),
        "root": str(DESKTOP_ROOT),
        "pages": [],
    }
    tracking_rows: list[str] = []
    html_paths: list[Path] = []
    public_paths: list[Path] = []

    for idx, page in enumerate(pages):
        spec = get_spec(page)
        page_key = page["slug"]
        scene_gallery = get_scene_gallery(page)
        scene_src = scene_gallery[0]
        food_src = food_assets[idx]

        ad_dir = ads_root / page_key
        wp_dir = wp_root / page_key
        for folder in (ad_dir, wp_dir):
            (folder / "assets").mkdir(parents=True, exist_ok=True)
            (folder / "preview-assets").mkdir(parents=True, exist_ok=True)

        ad_scene_dsts = [ad_dir / "assets" / f"scene-{i + 1:02d}-{src.name}" for i, src in enumerate(scene_gallery)]
        wp_scene_dsts = [wp_dir / "assets" / f"scene-{i + 1:02d}-{src.name}" for i, src in enumerate(scene_gallery)]
        ad_scene_preview_dsts = [ad_dir / "preview-assets" / f"gallery-{i + 1}.jpg" for i in range(len(scene_gallery))]
        wp_scene_preview_dsts = [wp_dir / "preview-assets" / f"gallery-{i + 1}.jpg" for i in range(len(scene_gallery))]
        ad_food_dst = ad_dir / "assets" / f"support-{food_src.name}"
        wp_food_dst = wp_dir / "assets" / f"support-{food_src.name}"
        ad_food_preview = ad_dir / "preview-assets" / "support.jpg"
        wp_food_preview = wp_dir / "preview-assets" / "support.jpg"

        for src, dst in [(food_src, ad_food_dst), (food_src, wp_food_dst)]:
            copy_asset(src, dst)

        for src, dst in zip(scene_gallery, ad_scene_dsts):
            copy_asset(src, dst)
        for src, dst in zip(scene_gallery, wp_scene_dsts):
            copy_asset(src, dst)

        for src, dst in zip(scene_gallery, ad_scene_preview_dsts):
            make_preview_image(src, dst)
        for src, dst in zip(scene_gallery, wp_scene_preview_dsts):
            make_preview_image(src, dst)
        for src, dst in [(food_src, ad_food_preview), (food_src, wp_food_preview)]:
            make_preview_image(src, dst)

        ad_brief = f"""# {page['title']} — Ad Pack

## Goal
{page['target_intent']}

## Audience
{page['audience']}

## Budget / people
- Budget range: {spec['budget_range']}
- Person range: {spec['person_range']}

## Source cases
{chr(10).join(f'- {case}' for case in page['source_cases'])}

## Source bridge
- 來源：3–5 月行事曆 + 報價單標題 + 現有素材
- 推斷：這一頁對應 {page['target_intent']}

## Creative notes
- Scene gallery:
{chr(10).join(f'- <相片 {asset.name}>' for asset in scene_gallery)}
- Headline angle: {spec['ad_angle']}
- CTA: 先以 LINE / 私訊 / 表單詢問為主

## TA setup
- Location: 台南 / 高雄
- Age: 25-45
- Objective: 以場景詢問與預約為主
- Exclusions: 無關低意圖流量
- Campaign note: ad draft only, do not publish yet

## Asset map
{chr(10).join(f'- {dst.name}' for dst in ad_scene_dsts)}
- {ad_food_dst.name}
"""
        ad_copy = render_ad_copy(page, spec, scene_gallery)
        ad_notes = f"""# {page['title']} — Ad Notes

- Campaign slug: {page['slug']}
- Keyword: {page['key_keyword']}
- Source cases: {", ".join(page['source_cases'])}
- Required action: draft only, no publish
- Angle: {spec['ad_angle']}
"""

        wp_brief = f"""# {page['title']} — WordPress Draft Pack

## Slug
{page['slug']}

## SEO keyword
{page['key_keyword']}

## Target intent
{page['target_intent']}

## Budget / people
- Budget range: {spec['budget_range']}
- Person range: {spec['person_range']}

## Structure
{chr(10).join(f'- {s}' for s in page['required_sections'])}

## Material slots
- Scene gallery:
{chr(10).join(f'- <相片 {asset.name}>' for asset in scene_gallery)}

## Source cases
{chr(10).join(f'- {case}' for case in page['source_cases'])}

## Source bridge
- 來源：3–5 月行事曆 + 報價單標題 + 現有素材
- 推斷：從案件名稱與日期回推活動類型，再對應到這一頁
"""
        wp_outline = f"""# {page['title']} — Outline

1. 開頭：直接講場景
2. 活動類型：這頁能支援哪些活動
3. 人數與預算：{spec['person_range']} / {spec['budget_range']}
4. 真實案例：對應 {", ".join(page['source_cases'][:2])}
5. FAQ：常見疑問
6. CTA：LINE / 詢問表單
7. 內連：連到同 cluster 的其他頁
"""
        wp_seo = f"""# {page['title']} — SEO Sheet

- Title: {page['title']}｜MAPLAB Kitchen
- Slug: {page['slug']}
- Focus keyword: {page['key_keyword']}
- Meta description: MAPLAB Kitchen 提供 {page['target_intent']} 的外燴與活動餐點規劃。
- Internal links: see related pages in launchpad
- Image alt slots:
{chr(10).join(f'  - <相片 {asset.name}>' for asset in scene_gallery)}
- Rank Math: see rankmath_payload.json
"""
        wp_copy = render_wp_draft(page, spec, scene_gallery)
        wp_internal = f"""# {page['title']} — Internal Links

This page should link to:
- related sibling pages in the same cluster: {", ".join(spec['internal_links'])}
- homepage / core service page
- relevant case-study posts
"""

        tracking_doc = render_tracking_note(page, spec)
        source_bridge = f"""# Source Bridge — {page['title']}

- Source sheet: {SOURCE_SHEET_URL}
- Inference rule: use date + quote title + existing asset context to infer activity type
- Selected cases: {", ".join(page['source_cases'])}
- Working assumption: this pack stays in draft/review until Owner approves
"""

        write_text(ad_dir / "brief.md", ad_brief)
        write_text(ad_dir / "copy.md", ad_copy)
        write_text(ad_dir / "ta.md", ad_notes)
        write_text(ad_dir / "asset_map.md", "\n".join(f"- {dst.name}" for dst in ad_scene_dsts) + f"\n- {ad_food_dst.name}\n")
        write_text(ad_dir / "source_bridge.md", source_bridge)

        write_text(wp_dir / "brief.md", wp_brief)
        write_text(wp_dir / "copy.md", wp_copy)
        write_text(wp_dir / "draft.md", wp_copy)
        write_text(wp_dir / "seo.md", wp_seo)
        write_text(wp_dir / "outline.md", wp_outline)
        write_text(wp_dir / "internal_links.md", wp_internal)
        write_text(wp_dir / "rankmath_payload.json", json.dumps(render_rankmath_payload(page, spec), ensure_ascii=False, indent=2))
        write_text(wp_dir / "source_bridge.md", source_bridge)
        write_text(wp_dir / "preview.html", render_preview_html(page, spec, scene_gallery))
        write_text(ad_dir / "preview.html", render_ads_preview_html(page, spec, scene_gallery))
        html_paths.extend([wp_dir / "preview.html", ad_dir / "preview.html"])
        public_paths.extend([wp_dir / "draft.md", wp_dir / "copy.md", wp_dir / "preview.html"])

        wp_prompt = render_openclaw_prompt(page, spec, wp_dir, "wordpress")
        ad_prompt = render_openclaw_prompt(page, spec, ad_dir, "ads")
        write_text(wp_dir / "openclaw_prompt.md", wp_prompt)
        write_text(wp_dir / "dispatch_prompt.md", wp_prompt)
        write_text(ad_dir / "openclaw_prompt.md", ad_prompt)
        write_text(ad_dir / "dispatch_prompt.md", ad_prompt)

        wp_run_cmd = jobs_root / f"run_wp_{page_key}.command"
        wp_schedule_cmd = jobs_root / f"schedule_wp_{page_key}.command"
        ad_run_cmd = jobs_root / f"run_ads_{page_key}.command"
        ad_schedule_cmd = jobs_root / f"schedule_ads_{page_key}.command"
        make_command_text(wp_run_cmd, render_run_command(wp_dir, "openclaw_prompt.md", f"JOB-WP-{page_key.upper()}"))
        make_command_text(wp_schedule_cmd, render_schedule_command(wp_dir, "openclaw_prompt.md", f"MAPLAB-WP-{page_key.upper()}"))
        make_command_text(ad_run_cmd, render_run_command(ad_dir, "openclaw_prompt.md", f"JOB-ADS-{page_key.upper()}"))
        make_command_text(ad_schedule_cmd, render_schedule_command(ad_dir, "openclaw_prompt.md", f"MAPLAB-ADS-{page_key.upper()}"))

        manifest["pages"].append(
            {
                "slug": page_key,
                "title": page["title"],
                "ad_folder": str(ad_dir),
                "wp_folder": str(wp_dir),
                "scene_source": str(scene_src),
                "food_source": str(food_src),
                "ad_assets": [dst.name for dst in ad_scene_dsts] + [ad_food_dst.name],
                "wp_assets": [dst.name for dst in wp_scene_dsts] + [wp_food_dst.name],
                "wp_run_command": str(wp_run_cmd),
                "wp_schedule_command": str(wp_schedule_cmd),
                "ad_run_command": str(ad_run_cmd),
                "ad_schedule_command": str(ad_schedule_cmd),
            }
        )
        tracking_rows.append(
            f"- {page['title']} | {page['slug']} | {page['key_keyword']} | {', '.join(page['source_cases'])} | {spec['budget_range']} | {spec['person_range']}"
        )

    write_text(
        DESKTOP_ROOT / "README.md",
        """# wordpress 素材庫

這是今天的 A2/A3 作業台。

## 內容

- `ads/`：5 個 B2B 廣告素材包
- `wordpress/`：5 個 B2B WordPress 草稿包（`draft.md` 為 public-safe；內部線索放在 `brief.md` / `source_bridge.md`）
- `tracking/`：像素 / 來源 / 欄位對應整理
- `jobs/`：OpenClaw run / schedule command
- `handoff.html`：可點擊任務面板

## 用法

先看 `handoff.html`，再看每個資料夾內的 `brief.md`、`copy.md`、`ta.md` 或 `seo.md`。

圖片已先放入 `assets/`，文案中的 `<相片 xxx>` 是要替換的位置。
每個 WordPress 文章包都包含 `draft.md` 和 `rankmath_payload.json`，可以直接交給 OpenClaw / GPT 做下一步整理；公開稿不得寫價格、內部日期或本機 Drive 路徑。
""",
    )
    write_text(
        tracking_root / "tracking_matrix.md",
        "# Tracking Matrix\n\n" + "\n".join(tracking_rows) + "\n",
    )
    write_text(
        tracking_root / "case_source_fields.md",
        """# Case Source Fields

案件日期｜案件名稱｜場景類型｜成交金額｜毛利估算｜客戶來源｜第一次接觸日期｜成交日期｜使用頁面｜廣告活動名稱｜是否可作案例
""",
    )
    write_text(
        tracking_root / "pixel_notes.md",
        """# Pixel Notes

- Meta Pixel: 228166994905799
- GTM Container: GTM-T2Z52GP
- Google Ads: 844-336-3178
- 先整理，不直接發布
""",
    )

    batch_prompt = render_nightly_batch_prompt(pages, Path.home() / "Desktop" / "MAPLAB_A2A3_Workbench")
    write_text(jobs_root / "nightly_batch_prompt.md", batch_prompt)
    make_command_text(
        jobs_root / "run_nightly_batch.command",
        render_run_command(jobs_root, "nightly_batch_prompt.md", "MAPLAB-NIGHTLY-A2A3"),
    )
    make_command_text(
        jobs_root / "schedule_nightly_batch.command",
        render_schedule_command(jobs_root, "nightly_batch_prompt.md", "MAPLAB-A2A3-nightly-batch"),
    )
    make_command_text(jobs_root / "run_openclaw_dashboard.command", "#!/bin/zsh\nopenclaw dashboard\n")
    write_text(
        jobs_root / "README.md",
        """# MAPLAB A2/A3 Jobs

這裡放每個工作包對應的 OpenClaw command。

## 用法

- `run_wp_*.command`：立即跑 WordPress 工作包
- `schedule_wp_*.command`：排到今晚 02:00
- `run_ads_*.command`：立即跑廣告工作包
- `schedule_ads_*.command`：排到今晚 02:00
- `run_nightly_batch.command`：一次處理整批
- `schedule_nightly_batch.command`：把整批排到今晚 02:00
- `run_openclaw_dashboard.command`：開 OpenClaw 控制台
""",
    )

    write_text(
        DESKTOP_ROOT / "README.md",
        """# wordpress 素材庫

這是今天的 A2/A3 作業台。

## 內容

- `ads/`：5 個 B2B 廣告素材包
- `wordpress/`：5 個 B2B WordPress 草稿包（`draft.md` 為 public-safe；內部線索放在 `brief.md` / `source_bridge.md`）
- `tracking/`：像素 / 來源 / 欄位對應整理
- `jobs/`：OpenClaw run / schedule command
- `handoff.html`：可點擊任務面板

## 用法

先看 `handoff.html`，再看每個資料夾內的 `brief.md`、`copy.md`、`ta.md` 或 `seo.md`。

圖片已先放入 `assets/`，文案中的 `<相片 xxx>` 是要替換的位置。
每個 WordPress 文章包都包含 `draft.md` 和 `rankmath_payload.json`，可以直接交給 OpenClaw / GPT 做下一步整理；公開稿不得寫價格、內部日期或本機 Drive 路徑。
""",
    )

    root_preview_links = "\n".join(
        f'<li><a href="wordpress/{page["slug"]}/preview.html">{page["title"]}</a></li>'
        for page in pages
    )
    write_text(
        DESKTOP_ROOT / "preview.html",
        f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>wordpress 素材庫 Preview</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; padding: 24px; background: #faf7f2; color: #1f2937; }}
    .card {{ background: #fff; border: 1px solid #e5ddd1; border-radius: 12px; padding: 18px; max-width: 960px; margin: 0 auto; }}
    ul {{ line-height: 1.8; }}
    a {{ color: #8b5e3c; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>wordpress 素材庫 Preview</h1>
    <p>打開每個 WordPress 草稿包的預覽頁，直接看圖、文案、FAQ 與 Rank Math 摘要。</p>
    <ul>
      {root_preview_links}
    </ul>
  </div>
</body>
</html>
""",
    )
    write_text(DESKTOP_ROOT / "publish-sim.html", render_publish_sim_html(pages))
    html_paths.extend([DESKTOP_ROOT / "preview.html", DESKTOP_ROOT / "publish-sim.html"])

    shortcut_dir = Path.home() / "Desktop" / "MAPLAB_A2A3_Workbench"
    shortcut_dir.mkdir(parents=True, exist_ok=True)
    (shortcut_dir / "04_open_wordpress_materials.command").write_text(
        "#!/bin/zsh\nopen '/Users/pagemacmini/Desktop/wordpress 素材庫'\n",
        encoding="utf-8",
    )
    (shortcut_dir / "05_open_wordpress_preview.command").write_text(
        "#!/bin/zsh\nopen '/Users/pagemacmini/Desktop/wordpress 素材庫/publish-sim.html'\n",
        encoding="utf-8",
    )
    os.chmod(shortcut_dir / "04_open_wordpress_materials.command", 0o755)
    os.chmod(shortcut_dir / "05_open_wordpress_preview.command", 0o755)
    make_command_text(shortcut_dir / "06_open_openclaw_dashboard.command", "#!/bin/zsh\nopenclaw dashboard\n")
    make_command_text(shortcut_dir / "07_open_handoff_board.command", "#!/bin/zsh\nopen '/Users/pagemacmini/Desktop/wordpress 素材庫/handoff.html'\n")

    (DESKTOP_ROOT / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    handoff_manifest = {
        "generated_at": "2026-05-11",
        "desktop_root": str(DESKTOP_ROOT),
        "preview_root": str(DESKTOP_ROOT / "preview.html"),
        "jobs_root": str(jobs_root),
        "pages": manifest["pages"],
        "nightly_batch_prompt": str(jobs_root / "nightly_batch_prompt.md"),
    }
    write_text(jobs_root / "handoff_manifest.json", json.dumps(handoff_manifest, ensure_ascii=False, indent=2))

    handoff_html = render_handoff_board_html(
        pages,
        DESKTOP_ROOT,
        DESKTOP_ROOT / "preview.html",
        jobs_root,
        jobs_root / "run_openclaw_dashboard.command",
    )
    write_text(DESKTOP_ROOT / "handoff.html", handoff_html)
    write_text(REPO / "docs" / "a2a3" / "handoff-board.html", handoff_html)
    html_paths.extend([DESKTOP_ROOT / "handoff.html", REPO / "docs" / "a2a3" / "handoff-board.html"])
    for optional_html in [
        DESKTOP_ROOT / "b2b-preview-index.html",
        REPO / "docs" / "a2a3" / "launchpad.html",
    ]:
        if optional_html.exists():
            html_paths.append(optional_html)

    for cmd_path in [jobs_root / "run_nightly_batch.command", jobs_root / "schedule_nightly_batch.command", jobs_root / "run_openclaw_dashboard.command"]:
        os.chmod(cmd_path, 0o755)

    verify_html_links(html_paths)
    verify_public_outputs(public_paths)

    print(f"Created workbench at: {DESKTOP_ROOT}")
    print(f"Pages: {len(pages)}")
    print(f"Gallery assets verified: {sum(len(get_scene_gallery(page)) for page in pages)}")
    print(f"Food assets used: {len(food_assets[:len(pages)])}")
    print(f"Verified HTML links: {len(html_paths)} files")
    print(f"Verified public outputs: {len(public_paths)} files")


if __name__ == "__main__":
    main()
