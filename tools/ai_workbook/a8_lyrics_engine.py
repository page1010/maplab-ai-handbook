#!/usr/bin/env python3
"""A8 音樂管線 v0：歌詞優先 + 可抽換唱後端.
核心價值＝歌詞創作＋品牌安全/品質審查（免費、本機可跑）。
唱＝後端 adapter（MiniMax API / Suno 人工），同一介面可切；實際呼叫待 Owner 給 key/帳號。
用法：python3 a8_lyrics_engine.py review <歌詞.txt> [--client 邦尼兔]
"""
import re, sys, os, json

# ---- 品牌安全字庫（沿用 brand-voice-guide + A8 教訓）----
BANNED = ["最頂","超值","保證","CP值","佛心","便宜又大碗","錯過可惜","趕快預約","名額有限","一生一次","不訂會後悔","限時優惠"]
A8_BANNED = ["取餐","順暢","分開","方便交流","促進交流","確保","動線穩","節奏更穩","節奏穩健"]
SOFT = ["精緻","質感","用心","客製化"]              # 少用（警告）
SENSITIVE = ["國旗","政治","總統","宗教","神明","種族","政黨","兩岸","統獨"]  # 敏感：國旗過貼那類雷，避免
POSITIVE_HINT = ["台南外燴","MAPLAB"]               # 建議自然置入

# ---- 中文押韻（十三轍）分析 ----
_ZHE_GROUPS = {
    "一七(i/ü)": "氣喜皮裡齊你米西記意力起級集例低題習句去語魚雨",
    "懷來(ai)": "愛乖嗨來戴懷白菜開台拜賽蓋派孩在還海",
    "言前(an)": "天面前邊年見甜點願線煙翻端安產感慢辦滿",
    "發花(a)": "啦家他花大媽怕阿沙抓吧茶掛畫",
    "江陽(ang)": "香上忙想場亮光唱樣幫湯牆胖旁",
    "中東(eng/ong/ing)": "紅夢風中情星應鐘空鬆種動用夢冷聲成",
    "人辰(en/in/un)": "心新人門神真春恩們沉分身信近今銀",
    "灰堆(ei/ui)": "美飛妹對誰淚給背黑北位嘴",
    "遙條(ao)": "高道好笑腳靠到抱早鬧巧包跑找號",
    "由求(ou)": "手口走有頭州收愁夠留丟秀",
    "姑蘇(u)": "路度樹步苦主哭部住福服",
    "梭波(o/e/uo)": "我河波過說課多錯坐火脆熱樂",
    "乜斜(ie/ue)": "街月也些節葉謝跌捷夜借",
}
ZHE = {ch: g for g, s in _ZHE_GROUPS.items() for ch in s}
def _zhe(ch): return ZHE.get(ch, "?")
def rhyme_words(zhe, n=10):
    for g, s in _ZHE_GROUPS.items():
        if g == zhe: return list(dict.fromkeys(s))[:n]
    return []
def analyze_rhyme(text):
    from collections import Counter
    sections, cur = {}, "_"
    for raw in text.splitlines():
        s = raw.strip()
        if not s: continue
        m = re.match(r'^\[([^\]]+)\]', s)
        if m:
            cur = m.group(1); sections.setdefault(cur, [])
            rest = s[m.end():].strip()
            if rest: sections[cur].append(rest)
            continue
        sections.setdefault(cur, []).append(s)
    per, total, rhymed, shuang = {}, 0, 0, 0
    for sec, lines in sections.items():
        rows = []
        for ln in lines:
            c = re.sub(r'[\s，。！？、,.!?/：:（）()【】\[\]]+', '', ln)
            rows.append({"line": ln, "e1": c[-1] if c else "", "z1": _zhe(c[-1]) if c else "?",
                         "e2": c[-2] if len(c) >= 2 else "", "z2": _zhe(c[-2]) if len(c) >= 2 else "?"})
        cnt = Counter(r["z1"] for r in rows if r["z1"] != "?")
        dom = cnt.most_common(1)[0][0] if cnt else "?"
        weak = []
        for i, r in enumerate(rows):
            total += 1
            r["ok"] = (r["z1"] == dom and dom != "?")
            if r["ok"]: rhymed += 1
            else: weak.append(r["line"])
            r["shuang"] = any(i != j and r["z1"] != "?" and r["z1"] == o["z1"] and r["z2"] != "?" and r["z2"] == o["z2"] for j, o in enumerate(rows))
            if r["shuang"]: shuang += 1
        per[sec] = {"dominant_zhe": dom, "weak_offrhyme": weak,
                    "ends": [f'{r["e2"]}{r["e1"]}({r["z1"]}{"+雙押" if r["shuang"] else ""})' for r in rows],
                    "suggest_words": rhyme_words(dom) if weak else []}
    return {"rhymed_ratio": round(rhymed/total, 2) if total else 0,
            "shuang_lines": shuang, "total_lines": total, "per_section": per,
            "hint": "弱的 weak_offrhyme 換同轍字(見 suggest_words)；相鄰行末兩字同轍=雙押,密度更高；但別為押韻犧牲順口/意思。"}

def _end_char(line): 
    s=re.sub(r"[\s，。！？、,.!?/\[\]（）()]+","",line); return s[-1] if s else ""

def review_lyrics(text, client=None):
    lines=[l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("[")]
    joined=text
    banned=[w for w in BANNED+A8_BANNED if w in joined]
    soft=[w for w in SOFT if w in joined]
    sensitive=[w for w in SENSITIVE if w in joined]
    has_hook=("[hook]" in text.lower()) or ("[chorus]" in text.lower())
    has_verse="[Verse]" in text or "[verse]" in text.lower()
    ends=[_end_char(l) for l in lines]
    # 簡易押韻提示：相鄰行尾字相同者
    rhyme_pairs=sum(1 for i in range(len(ends)-1) if ends[i] and ends[i]==ends[i+1])
    brand_in=[w for w in POSITIVE_HINT if w in joined]
    client_flag=[]
    if client and client not in joined:
        client_flag.append(f"未出現客戶名「{client}」——確認是否要置入(且客戶名需先查證)")
    ok = (not banned) and has_hook and has_verse
    return {
        "ok": ok,
        "banned_hits": banned,                 # 有＝擋(必修)
        "sensitive_hits": sensitive,           # 有＝人工判斷(國旗/政治那類雷)
        "soft_overuse": soft,                  # 少用詞提醒
        "structure": {"has_hook":has_hook,"has_verse":has_verse},
        "rhyme_pairs_hint": rhyme_pairs,       # 越多越有押韻感(提示,非硬標準)
        "brand_placed": brand_in,              # 是否置入 台南外燴/MAPLAB
        "client_name_flags": client_flag,
        "line_count": len(lines),
        "rhyme": analyze_rhyme(text),
        "human_checklist": [                   # 歌詞優先＝人做最終審(做厚這段)
            "俏皮/有記憶點？","雙押韻順不順口？","不傷品牌(無禁用詞/不低價)？",
            "無業主/賓客敏感、無過貼國旗政治？","客戶名已查證？","自然置入 台南外燴/MAPLAB？",
        ],
    }

# ---- 可抽換唱後端（同一介面）----
class SingBackend:
    name="base"
    def generate(self, lyrics, style, out_path=None): raise NotImplementedError

class MiniMaxBackend(SingBackend):
    """主力試錯：MiniMax Music 3.0，有官方 API、$0.15/首、可自動化。實呼叫待 API key。"""
    name="minimax"
    def generate(self, lyrics, style, out_path=None):
        key=os.environ.get("MINIMAX_API_KEY")
        if not key:
            return {"status":"needs_key","backend":"minimax",
                    "how":"把 MiniMax API key 放進 Notion 憑證庫欄位 MINIMAX_API_KEY(或 bot/.env)，我再接",
                    "endpoint_hint":"MiniMax 官方 music API 或 fal.ai/models/fal-ai/minimax-music；payload=lyrics([Verse]/[Chorus] tags)+style",
                    "cost":"$0.15/首(≤5分)；有 free 層(有限)"}
        # TODO: 有 key 後在此接 API（requests.post endpoint, {lyrics, style}）→ 存 out_path
        return {"status":"stub_ready","backend":"minimax"}

class SunoBackend(SingBackend):
    """商用定版：Suno Pro，商用權清楚、可下載，但無官方 API＝人工。"""
    name="suno"
    def generate(self, lyrics, style, out_path=None):
        return {"status":"manual","backend":"suno",
                "how":"Owner 登入 Suno→Custom Mode 貼歌詞+曲風(%s)→生成→下載，再餵管線"%style,
                "commercial":"Pro 商用權清楚"}

BACKENDS={"minimax":MiniMaxBackend(),"suno":SunoBackend()}
def get_backend(name="minimax"): return BACKENDS[name]

def run(lyrics, client=None, backend="minimax", style="中文 boom bap 饒舌"):
    r=review_lyrics(lyrics, client)
    if not r["ok"]:
        return {"stage":"review_failed","review":r}   # 定稿才送生成
    gen=get_backend(backend).generate(lyrics, style)
    return {"stage":"sent_to_backend","review":r,"backend_result":gen}

# ---- 中性創意 DB（不綁供應商）----
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "workbook", "a8", "music_creative_db.json")
def load_db():
    return json.load(open(DB_PATH, encoding="utf-8"))
def get_entry(eid):
    for e in load_db().get("entries", []):
        if e["id"] == eid: return e
    return None
def make_suno_pack(eid, variant=None):
    """產 paste-ready Suno 包：曲風欄 + 歌詞欄，可直接貼進 Suno 網頁。"""
    e = get_entry(eid)
    if not e: return f"找不到 {eid}"
    ep = e["engine_prompts"]
    style = ep["suno"] if not variant else ep.get("suno_variants", {}).get(variant, ep["suno"])
    lyr = e.get("suno_lyrics", e["lyrics_reviewed"])
    tag = f"（{variant}）" if variant else ""
    return (f"🎵 Suno 貼上包｜{e['id']}{tag}\n"
            f"vibe：{e['vibe']}\n\n"
            f"🔮 預計產出風格：{e.get('expected_style','')}\n\n"
            f"① 曲風/Style 欄貼這段：\n{style}\n\n"
            f"② 歌詞/Lyrics 欄貼這段（含 meta-tag/vocal cue）：\n{lyr}\n\n"
            f"（先用 Suno 免費層試品質：有浮水印、非商用；對味再升 Pro $10/月(年繳$96/年、省20%)＝商用＋可下載＋無浮水印。訂閱由 Owner 決定。）")

if __name__=="__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "review" and len(sys.argv) >= 3:
        client = sys.argv[sys.argv.index("--client")+1] if "--client" in sys.argv else None
        print(json.dumps(review_lyrics(open(sys.argv[2]).read(), client), ensure_ascii=False, indent=2))
    elif cmd == "suno-pack" and len(sys.argv) >= 3:
        variant = sys.argv[sys.argv.index("--variant")+1] if "--variant" in sys.argv else None
        print(make_suno_pack(sys.argv[2], variant))
    elif cmd == "db":
        for e in load_db().get("entries", []):
            print(e["id"], "|", e["concept"], "| status:", e.get("status"))
    else:
        print("usage:\n  review <lyrics.txt> [--client 名稱]\n  suno-pack <id> [--variant trap|lofi]\n  db")
