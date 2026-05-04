#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import textwrap
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from jsonschema import validate
from jsonschema.exceptions import ValidationError


BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
SCHEMA_DIR = BASE_DIR / "schemas"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output" / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(raw: str) -> str:
    clean = re.sub(r"[^a-z0-9\-]+", "-", raw.lower()).strip("-")
    return re.sub(r"-{2,}", "-", clean)


@dataclass
class FactoryConfig:
    ollama_base_url: str
    model_small: str
    model_medium: str
    wp_base_url: Optional[str]
    wp_username: Optional[str]
    wp_app_password: Optional[str]
    publish_enabled: bool
    ollama_timeout_seconds: int


class OllamaClient:
    def __init__(self, cfg: FactoryConfig):
        self.base_url = cfg.ollama_base_url.rstrip("/")
        self.model_small = cfg.model_small
        self.model_medium = cfg.model_medium
        self.timeout_seconds = cfg.ollama_timeout_seconds

    def generate(self, prompt: str, medium: bool = False) -> str:
        model = self.model_medium if medium else self.model_small
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=self.timeout_seconds,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "").strip()
            return text or self._fallback(prompt)
        except Exception:
            return self._fallback(prompt)

    @staticmethod
    def _fallback(prompt: str) -> str:
        return f"[FALLBACK_OUTPUT]\n{prompt[:1200]}"


class Planner:
    def run(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        sections = [
            {"section": s, "goal": f"Cover {s} for {brief['target_intent']} intent."}
            for s in brief["required_sections"]
        ]
        return {
            "pillar": brief["pillar"],
            "slug": brief["slug"],
            "outline": sections,
            "intent": brief["target_intent"],
            "audience": brief["audience"],
            "banned_topics": brief["banned_topics"],
        }


class Writer:
    def __init__(self, ollama: OllamaClient):
        self.ollama = ollama

    def run(self, plan: Dict[str, Any], focus_keyword: str) -> Dict[str, Any]:
        prompt = textwrap.dedent(
            f"""
            Write a structured Chinese markdown landing page draft.
            Intent: {plan['intent']}
            Audience: {plan['audience']}
            Focus keyword: {focus_keyword}
            Required sections: {', '.join([s['section'] for s in plan['outline']])}
            Avoid: {', '.join(plan['banned_topics'])}
            Must include conversion-first CTA.
            """
        ).strip()
        body = self.ollama.generate(prompt, medium=True)
        if body.startswith("[FALLBACK_OUTPUT]"):
            body = self._fallback_body(plan, focus_keyword)
        title = self._title_for(plan["pillar"])
        faq_items = self._faq_for(plan["pillar"])
        cta = "想要拿到符合活動預算與人數的提案，立即私訊 MAPLAB Kitchen 預約諮詢。"
        meta = {
            "focus_keyword": focus_keyword,
            "title": f"{title}｜MAPLAB Kitchen",
            "description": "MAPLAB Kitchen 提供台南高質感外燴規劃，從菜單、動線到現場服務一站式完成。",
        }
        return {
            "slug": slugify(plan["slug"]),
            "title": title,
            "body_md": body,
            "faq_items": faq_items,
            "cta": cta,
            "meta": meta,
        }

    @staticmethod
    def _title_for(pillar: str) -> str:
        mapping = {
            "corporate": "台南企業外燴服務指南：會議點心、開幕茶會與品牌活動",
            "birthday": "台南週歲派對外燴指南：抓周、生日與家庭聚會一次規劃",
            "wedding": "台南婚禮外燴指南：戶外婚禮與迎賓茶點整合方案",
        }
        return mapping.get(pillar, "MAPLAB Kitchen 外燴服務")

    @staticmethod
    def _faq_for(pillar: str) -> List[Dict[str, str]]:
        common = [
            {"q": "最早需要多久前預約？", "a": "建議至少提前 2-4 週預約，熱門檔期請更早確認。"},
            {"q": "可以客製菜單與預算嗎？", "a": "可以，會依活動人數、情境與預算區間做客製化提案。"},
            {"q": "服務區域只有台南嗎？", "a": "主要服務台南與周邊，跨區可依場次規模另行評估。"},
        ]
        if pillar == "corporate":
            common.append(
                {
                    "q": "企業發表會可以做品牌視覺整合嗎？",
                    "a": "可以，會配合活動主題規劃餐檯風格、色系與動線，確保品牌感一致。",
                }
            )
        elif pillar == "birthday":
            common.append(
                {
                    "q": "抓周儀式與餐點流程可以整合嗎？",
                    "a": "可以，會先對齊儀式時間軸與上菜節點，避免流程卡住並兼顧長輩與小孩體驗。",
                }
            )
        elif pillar == "wedding":
            common.append({"q": "戶外婚禮遇雨怎麼辦？", "a": "會預先規劃雨備動線與備案，確保流程不受影響。"})
        return common

    @staticmethod
    def _fallback_body(plan: Dict[str, Any], focus_keyword: str) -> str:
        section_md = "\n\n".join(
            [f"## {item['section']}\n\n針對 {focus_keyword}，本段提供可直接執行的活動規劃要點與範例。" for item in plan["outline"]]
        )
        return (
            f"# {focus_keyword}\n\n"
            f"MAPLAB Kitchen 以高質感服務流程，協助你完成 {plan['intent']}。\n\n"
            f"{section_md}\n\n"
            "## CTA\n\n立即聯繫 MAPLAB Kitchen，取得對應人數與預算的客製外燴提案。"
        )


class Linker:
    def __init__(self, link_policy: Dict[str, Any]):
        self.policy = link_policy

    def run(self, pillar: str) -> List[Dict[str, str]]:
        cluster = next((c for c in self.policy["clusters"] if c["cluster"] == pillar), None)
        if not cluster:
            return []
        targets = cluster["allowed_targets"][: self.policy["max_links_per_doc"]]
        link_types = (
            ["exact_match"] * max(1, int(len(targets) * self.policy["anchor_mix"]["exact_match"]))
            + ["semantic_related"] * max(1, int(len(targets) * self.policy["anchor_mix"]["semantic_related"]))
            + ["brand_generic"] * max(1, int(len(targets) * self.policy["anchor_mix"]["brand_generic"]))
        )
        links = []
        for idx, url in enumerate(targets):
            anchor_type = link_types[idx % len(link_types)]
            links.append(
                {
                    "anchor_text": self._anchor_text(pillar, anchor_type),
                    "url": url,
                    "position_hint": "early-body" if idx < 2 else "mid-body",
                    "anchor_type": anchor_type,
                }
            )
        return links

    @staticmethod
    def _anchor_text(pillar: str, anchor_type: str) -> str:
        exact = {
            "corporate": "台南企業外燴",
            "birthday": "台南週歲派對外燴",
            "wedding": "台南婚禮外燴",
        }
        semantic = {
            "corporate": "企業茶會與品牌活動餐飲規劃",
            "birthday": "抓周與家庭派對外燴流程",
            "wedding": "戶外婚禮與迎賓茶點整合",
        }
        brand = {
            "corporate": "MAPLAB 企業方案",
            "birthday": "MAPLAB 家庭派對方案",
            "wedding": "MAPLAB 婚禮方案",
        }
        if anchor_type == "exact_match":
            return exact[pillar]
        if anchor_type == "semantic_related":
            return semantic[pillar]
        return brand[pillar]


class SchemaBuilder:
    def run(self, brief: Dict[str, Any], draft: Dict[str, Any]) -> List[Dict[str, Any]]:
        page_url = f"https://www.maplabkitchen.com/{draft['slug']}/"
        service_name = draft["title"]
        base = {
            "@context": "https://schema.org",
            "@type": "FoodService",
            "name": "MAPLAB Kitchen",
            "url": "https://www.maplabkitchen.com/",
            "areaServed": "Tainan",
            "servesCuisine": ["Buffet", "Dessert", "Modern Catering"],
            "acceptsReservations": "True",
            "hasMenu": "https://www.maplabkitchen.com/menu/",
        }
        service = {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": service_name,
            "provider": {"@type": "FoodService", "name": "MAPLAB Kitchen"},
            "areaServed": "Tainan",
            "url": page_url,
            "audience": {"@type": "Audience", "audienceType": brief["audience"]},
        }
        faq = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": i["q"], "acceptedAnswer": {"@type": "Answer", "text": i["a"]}}
                for i in draft["faq_items"]
            ],
        }
        return [base, service, faq]


class Verifier:
    def __init__(self):
        self.content_brief_schema = read_json(SCHEMA_DIR / "content_brief.schema.json")
        self.draft_schema = read_json(SCHEMA_DIR / "draft_artifact.schema.json")

    def validate_brief(self, brief: Dict[str, Any]) -> Optional[str]:
        try:
            validate(instance=brief, schema=self.content_brief_schema)
            return None
        except ValidationError as e:
            return e.message

    def validate_draft(self, artifact: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        failures: List[str] = []
        try:
            validate(instance=artifact, schema=self.draft_schema)
        except ValidationError as e:
            failures.append(f"schema:{e.message}")
        if len(artifact.get("meta", {}).get("description", "")) > 160:
            failures.append("meta_description_too_long")
        if len(artifact.get("internal_links", [])) > 8:
            failures.append("too_many_internal_links")
        score = max(0, 100 - len(failures) * 20)
        return len(failures) == 0, {"pass": len(failures) == 0, "score": score, "failures": failures, "auto_fixable": failures}


class WordPressPublisher:
    def __init__(self, cfg: FactoryConfig):
        self.cfg = cfg
        self.publish_schema = read_json(SCHEMA_DIR / "publish_payload.schema.json")

    def build_payload(self, draft: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        content = draft["body_md"] + "\n\n## 常見問題\n\n" + "\n".join([f"- **{x['q']}**：{x['a']}" for x in draft["faq_items"]])
        content += f"\n\n## 諮詢\n\n{draft['cta']}"
        payload = {
            "post_id": None,
            "status": "draft",
            "content": content,
            "meta_fields": {
                "rank_math_focus_keyword": draft["meta"]["focus_keyword"],
                "rank_math_title": draft["meta"]["title"],
                "rank_math_description": draft["meta"]["description"],
            },
            "trace_id": trace_id,
        }
        validate(instance=payload, schema=self.publish_schema)
        return payload

    def publish(self, draft: Dict[str, Any], trace_id: str, dry_run: bool = True) -> Dict[str, Any]:
        payload = self.build_payload(draft, trace_id)
        if dry_run or not self.cfg.publish_enabled:
            return {"mode": "dry-run", "payload": payload}
        auth = base64.b64encode(f"{self.cfg.wp_username}:{self.cfg.wp_app_password}".encode("utf-8")).decode("utf-8")
        endpoint = f"{self.cfg.wp_base_url.rstrip('/')}/wp-json/wp/v2/posts"
        req_payload = {
            "title": draft["title"],
            "slug": draft["slug"],
            "status": "draft",
            "content": payload["content"],
            "meta": payload["meta_fields"],
        }
        resp = requests.post(
            endpoint,
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json",
                "X-MAPLAB-Trace-ID": trace_id,
            },
            data=json.dumps(req_payload, ensure_ascii=False).encode("utf-8"),
            timeout=60,
        )
        if not resp.ok:
            return {"mode": "live", "ok": False, "status_code": resp.status_code, "text": resp.text[:1200]}
        data = resp.json()
        return {"mode": "live", "ok": True, "post_id": data.get("id"), "link": data.get("link"), "status": data.get("status")}


class Auditor:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def add(self, stage: str, payload: Dict[str, Any]) -> None:
        self.records.append({"at": utc_now(), "stage": stage, "payload": payload})

    def dump(self) -> List[Dict[str, Any]]:
        return self.records


class CannibalizationReporter:
    def run(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for row in signals:
            key = row.get("intent_key", "").strip()
            if not key:
                continue
            grouped.setdefault(key, []).append(row)
        candidates = []
        for intent_key, rows in grouped.items():
            if len(rows) < 2:
                continue
            sorted_rows = sorted(rows, key=lambda x: (x.get("clicks", 0), x.get("impressions", 0)), reverse=True)
            canonical = sorted_rows[0]
            merge_sources = sorted_rows[1:]
            candidates.append(
                {
                    "intent_key": intent_key,
                    "canonical_winner": canonical["url"],
                    "merge_sources": [r["url"] for r in merge_sources],
                    "recommended_redirects": [{"from": r["url"], "to": canonical["url"], "code": 301} for r in merge_sources],
                    "notes": "Human approval required before redirect write.",
                }
            )
        return {"generated_at": utc_now(), "count": len(candidates), "candidates": candidates}


def load_factory_config(publish_enabled: bool) -> FactoryConfig:
    return FactoryConfig(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        model_small=os.getenv("OLLAMA_MODEL_SMALL", "llama3.1:latest"),
        model_medium=os.getenv("OLLAMA_MODEL_MEDIUM", "llama3.1:latest"),
        wp_base_url=os.getenv("WP_BASE_URL"),
        wp_username=os.getenv("WP_USERNAME"),
        wp_app_password=os.getenv("WP_APP_PASSWORD"),
        publish_enabled=publish_enabled,
        ollama_timeout_seconds=int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45")),
    )


def run_factory(publish: bool = False, pillars_filter: Optional[List[str]] = None) -> Dict[str, Any]:
    cfg = load_factory_config(publish_enabled=publish)
    trace_id = f"seo-factory-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    run_dir = OUTPUT_DIR / trace_id
    artifacts_dir = run_dir / "artifacts"
    reports_dir = run_dir / "reports"

    pillars = read_json(CONFIG_DIR / "pillars.json")["pillars"]
    if pillars_filter:
        wanted = set([x.strip().lower() for x in pillars_filter if x.strip()])
        pillars = [p for p in pillars if p.get("pillar", "").lower() in wanted]
    link_policy = read_json(CONFIG_DIR / "link_policy.json")
    signals_path = INPUT_DIR / "post_signals_sample.json"
    signals = read_json(signals_path).get("signals", []) if signals_path.exists() else []

    ollama = OllamaClient(cfg)
    planner = Planner()
    writer = Writer(ollama)
    linker = Linker(link_policy)
    schemer = SchemaBuilder()
    verifier = Verifier()
    publisher = WordPressPublisher(cfg)
    auditor = Auditor()
    cannibal = CannibalizationReporter()

    validation_summary = []
    publishing_summary = []

    for brief in pillars:
        brief_error = verifier.validate_brief(brief)
        if brief_error:
            auditor.add("brief_validation_failed", {"pillar": brief.get("pillar"), "error": brief_error})
            validation_summary.append({"pillar": brief.get("pillar"), "pass": False, "score": 0, "failures": [brief_error], "auto_fixable": []})
            continue
        plan = planner.run(brief)
        auditor.add("planner", {"pillar": brief["pillar"], "sections": len(plan["outline"])})

        draft = writer.run(plan, brief["focus_keyword"])
        auditor.add("writer", {"pillar": brief["pillar"], "chars": len(draft["body_md"])})

        links = linker.run(brief["pillar"])
        draft["internal_links"] = links
        auditor.add("linker", {"pillar": brief["pillar"], "links": len(links)})

        draft["schema_jsonld"] = schemer.run(brief, draft)
        auditor.add("schema_builder", {"pillar": brief["pillar"], "schema_blocks": len(draft["schema_jsonld"])})

        is_valid, report = verifier.validate_draft(draft)
        validation_summary.append({"pillar": brief["pillar"], **report})
        auditor.add("verifier", {"pillar": brief["pillar"], **report})

        write_json(artifacts_dir / f"pillar-draft-{brief['pillar']}.json", draft)

        result = publisher.publish(draft, trace_id, dry_run=not publish)
        publishing_summary.append({"pillar": brief["pillar"], "result": result})
        auditor.add("publisher", {"pillar": brief["pillar"], "mode": result.get("mode"), "ok": result.get("ok", True)})

        auditor.add("auditor", {"pillar": brief["pillar"], "trace_id": trace_id, "valid": is_valid})

    cannibal_report = cannibal.run(signals)
    write_json(reports_dir / "cannibalization-candidates.json", cannibal_report)
    write_json(reports_dir / "validation-summary.json", {"trace_id": trace_id, "items": validation_summary})
    write_json(reports_dir / "publishing-summary.json", {"trace_id": trace_id, "items": publishing_summary})
    write_json(reports_dir / "audit-log.json", {"trace_id": trace_id, "records": auditor.dump()})

    return {
        "trace_id": trace_id,
        "run_dir": str(run_dir),
        "pillars_processed": len(pillars),
        "validation": validation_summary,
        "publishing": publishing_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MAPLAB local SEO content factory.")
    parser.add_argument("--publish", action="store_true", help="Publish WordPress drafts (requires WP env vars).")
    parser.add_argument(
        "--pillars",
        type=str,
        default="",
        help="Optional comma-separated pillars to run, e.g. corporate,birthday,wedding",
    )
    args = parser.parse_args()
    selected = [x for x in args.pillars.split(",") if x.strip()] if args.pillars else None
    result = run_factory(publish=args.publish, pillars_filter=selected)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
