import sys
import json
from pathlib import Path

# Add bot_a6 to path so we can import modules
ROOT = Path("/Users/pagemacmini/maplab-ai-handbook")
sys.path.insert(0, str(ROOT / "bot_a6"))

from a5_quote_engine import run_a5_local_quote
from bot_a6 import _extract_form_data

TEST_CASES = [
    "報價 李晴宜 週歲抓周 20人 15000含10%服務費 12/21 上午11點 台南安南區安和路三段190巷 室內冷氣房 自家畫廊 不要羊 部分長輩不吃牛串燒可以 輕食A",
    "報價 洪炳輝 入厝 30人 3萬含10%服務費 10/25 下午五點半 安南區安興街351巷60號 半戶外車庫 主食B 無禁忌",
    "報價 Gina浥慧 企業開幕 30-40人 12000 11/9 早上十點到下午五點 安平區慶平路440號 室內一樓 茶點為主",
    "外帶 范純禎 11/29 下午兩點半 她自己會叫Lalamove來拿 漢堡排45入 蛋沙拉可頌60入 鹹派3個切8 小圓鬆餅120顆 烤布丁60個 她算15885",
    "報價 林韋如 入厝 50人 九萬含服務費車馬 3/9 中午十二點到三點 新營區中正路551巷 戶外 主食B",
    "報價 張雅淳 證婚儀式 70-80人 Candy bar 19800 3/22 下午一點到四點半 王老爹的開心農場 只要甜點不要鹹食",
    "報價 台北科技大學 研討會 100人 4萬 10/10 早上九點到下午一點 台北大安區 室內 主食",
    "報價 王小明 婚禮 80人 預算6萬",
    "報價 李四 尾牙 50人 預算5萬 12/31 晚上",
    "報價 張三 茶會 20人 預算10000 隨便配",
]

def run_tests():
    success_count = 0
    fail_count = 0

    for i, user_message in enumerate(TEST_CASES, 1):
        print(f"\n{'='*50}\nRound {i}: {user_message}\n{'='*50}")
        
        result = run_a5_local_quote(user_message, "TestRunner", [])
        answer = result.answer
        
        form_data = _extract_form_data(answer)
        
        if form_data and form_data.get("action") == "createQuote":
            print("✅ PASSED: JSON block detected and valid.")
            print(f"Extracted: {json.dumps(form_data, ensure_ascii=False)}")
            success_count += 1
        elif "外帶" in user_message and not form_data:
            print("✅ PASSED: Expected no quote JSON for takeout.")
            success_count += 1
        else:
            print("❌ FAILED: JSON block missing or invalid.")
            print(f"--- Output Snippet ---\n{answer}\n--------------------")
            fail_count += 1

    print(f"\nTest Summary: {success_count}/{len(TEST_CASES)} passed, {fail_count} failed.")
    
    if fail_count == 0:
        print("✅ 10-round local model quotation simulation passed.")
    else:
        print("⚠️ Model needs prompt optimization.")

if __name__ == "__main__":
    run_tests()
