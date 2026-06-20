const FALLBACK_DATA = {
  roles: [
    {
      role_id: "A0",
      name: "Dispatch Secretary",
      purpose: "跨系統調度、Telegram/Chrome/connector 入口、把任務派給 A1 或專門角色。",
      capabilities: ["dispatch", "handoff", "connector_bridge"],
      preferred_runtimes: ["codex", "chrome_extension", "telegram"],
      links: ["AGENT_RULES.md#section-13--a0"]
    },
    {
      role_id: "A1",
      name: "System Orchestrator",
      purpose: "治理、版本紀錄、runtime panel、任務卡、checkpoint 與 repo 事實核對。",
      capabilities: ["git_governance", "runtime_audit", "first_principles_debug"],
      preferred_runtimes: ["codex", "claude_code"]
    },
    {
      role_id: "A5",
      name: "Quotation Engine",
      purpose: "報價邏輯、菜單、毛利、品項資料；只處理報價事實，不負責客戶語氣。",
      capabilities: ["quote_math", "menu_mapping", "margin_guard"],
      preferred_runtimes: ["codex", "gas_sheet", "ollama_fallback"]
    },
    {
      role_id: "A6",
      name: "Sales Rapid Response",
      purpose: "急件對話、案件摘要、Telegram/LINE 接口；一般聊天 Codex-first，額度不足才 Ollama。",
      capabilities: ["case_store", "telegram_delivery", "quote_routing"],
      preferred_runtimes: ["codex_primary", "ollama_fallback", "openclaw_review"]
    },
    {
      role_id: "A7",
      name: "Customer Reply",
      purpose: "把 A5/A6 的事實改成可直接給客戶看的語氣與補問流程。",
      capabilities: ["reply_tone", "faq", "missing_info_questions"],
      preferred_runtimes: ["codex", "gpt"]
    },
    {
      role_id: "B1",
      name: "Investment Logic Bridge",
      purpose: "召喚 Investment OS 的投資人格、左側/右側/風控框架；暫停內容發文，不下單。",
      capabilities: ["persona_bridge", "risk_language", "research_prompt"],
      preferred_runtimes: ["codex", "chrome_extension", "investment_os"]
    },
    {
      role_id: "RISK",
      name: "風險大師",
      purpose: "regime、總曝險、1R、失效點、保險與黑天鵝優先級。",
      capabilities: ["regime_check", "position_risk", "invalidation"],
      preferred_runtimes: ["investment_os", "codex"]
    },
    {
      role_id: "LEFT",
      name: "左側經理人",
      purpose: "世界觀、終局、預期差、催化、非對稱下注與小部位規則。",
      capabilities: ["narrative_gap", "catalyst_map", "left_side_guard"],
      preferred_runtimes: ["investment_os", "codex"]
    },
    {
      role_id: "RIGHT",
      name: "右側經理人",
      purpose: "市場是否同意、突破、回測、主升段、分批加減碼與時間出場。",
      capabilities: ["right_side_scan", "technical_confirmation", "chip_check"],
      preferred_runtimes: ["investment_os", "codex"]
    }
  ],
  pipelines: [
    {
      pipeline_id: "maplab_a6_quote",
      name: "A6 急件報價路徑",
      steps: [
        { id: "intake", input_type: "Telegram/LINE message", output_type: "Case summary" },
        { id: "route_guard", input_type: "Case summary", output_type: "Chat / Quote / CaseStore route" },
        { id: "a5_quote", input_type: "Quote request", output_type: "Menu + price + margin notes" },
        { id: "a7_reply", input_type: "Facts", output_type: "Customer-ready reply draft" },
        { id: "approval", input_type: "Draft", output_type: "Owner/Mina approved action" }
      ]
    },
    {
      pipeline_id: "investment_os_research",
      name: "Investment OS 研究路徑",
      steps: [
        { id: "theme_stage", input_type: "Worldview / news / scan seed", output_type: "Theme thesis" },
        { id: "fact_check", input_type: "Thesis", output_type: "Verified facts / missing data" },
        { id: "risk_left_right", input_type: "Facts", output_type: "Risk + left + right review" },
        { id: "owner_brief", input_type: "Review", output_type: "Action buckets + invalidation" }
      ]
    },
    {
      pipeline_id: "memory_feedback_loop",
      name: "外部記憶回收路徑",
      steps: [
        { id: "session_end", input_type: "Work result", output_type: "Commit + resume prompt" },
        { id: "pitfall_capture", input_type: "Repeated failure", output_type: "pitfalls.md lesson" },
        { id: "role_module_sync", input_type: "Role change", output_type: "Chrome Extension module" },
        { id: "panel_refresh", input_type: "New surface", output_type: "Visible entrypoint" }
      ]
    },
    {
      pipeline_id: "hermes_patrol_reaction",
      name: "每日巡查反應路徑",
      steps: [
        { id: "collect", input_type: "scripts/patrol.sh output", output_type: "Raw patrol text" },
        { id: "packet", input_type: "Raw patrol text + task cards", output_type: "workbook/hermes/patrol/latest.json" },
        { id: "react", input_type: "Hermes packet", output_type: "Role owner + next action + memory candidate" },
        { id: "dispatch", input_type: "Reaction card", output_type: "Codex/A1/B1 follow-up prompt or Owner 5-minute card" }
      ]
    }
  ]
};

const PANEL_DATA = {
  launchers: [
    {
      label: "雙擊重開",
      command: "/Users/pagemacmini/maplab-ai-handbook/open-agent-runtime-panel.command"
    },
    {
      label: "終端機重開",
      command: "/Users/pagemacmini/maplab-ai-handbook/scripts/open_agent_runtime_panel.sh open"
    },
    {
      label: "Hermes 巡查面板",
      command: "/Users/pagemacmini/maplab-ai-handbook/scripts/open_agent_runtime_panel.sh hermes"
    },
    {
      label: "Finder 顯示位置",
      command: "/Users/pagemacmini/maplab-ai-handbook/scripts/open_agent_runtime_panel.sh reveal"
    }
  ],
  surfaces: [
    {
      name: "Repo Panel",
      status: "P0 live",
      body: "固定 HTML 入口。關掉後從 .command、README 或 Desktop shortcut 重開。",
      links: [
        ["Panel HTML", "./panel.html"],
        ["README", "./README.md"],
        ["Roadmap", "../projects/cross-project-agent-runtime-roadmap.md"]
      ]
    },
    {
      name: "Chrome Extension Role Recall",
      status: "B1 updated",
      body: "用側邊欄召喚角色時，B1 已改成 Investment OS 邏輯橋接，不再是 InnerFlowLab 發文角色。",
      links: [
        ["Extension folder", "../chrome-extension/"],
        ["B1 canonical", "../projects/b1-investment-os-owner-persona-canonical.md"],
        ["B1 profile", "../projects/b1-investment-os-owner-profile.md"]
      ]
    },
    {
      name: "Telegram / A6",
      status: "Codex-first",
      body: "一般聊天與 SEO 問題先接 Codex；明確報價才進 A5；Codex 不可用才切本機 Ollama。",
      links: [
        ["A6 bot", "../bot_a6/bot_a6.py"],
        ["Line quote assistant", "../projects/line-quote-assistant.md"],
        ["Current status", "../CURRENT_STATUS.md"]
      ]
    },
    {
      name: "Hermes Patrol Reaction",
      status: "Packet + panel",
      body: "每日巡查先由 bash 採集，再產 Hermes reaction packet；Hermes/Chrome Extension/Codex 讀 packet 做派工、記憶候選與角色下一步。",
      links: [
        ["Hermes panel", "./hermes.html"],
        ["Latest packet", "../workbook/hermes/patrol/latest.md"],
        ["Hermes prompt", "../workbook/hermes/patrol/hermes_prompt.md"]
      ]
    }
  ],
  takeaways: [
    {
      title: "Durable thread 要搭配外部記憶",
      text: "長對話可以保留工作脈絡，但真正不能丟的是 repo 文件、task card、pitfalls、case store 與可核對連結。",
      tags: ["pinned thread", "external memory", "git"]
    },
    {
      title: "Goal 必須有驗收點",
      text: "不要只說繼續做，要寫清楚 done 是什麼：測試、Telegram 收到、面板能重開、連結不壞。",
      tags: ["goal", "oracle", "verification"]
    },
    {
      title: "可視化介面要有重開路徑",
      text: "一次性 HTML 的問題不是不好用，是關掉後失去入口。這版改成 repo path + .command + Desktop shortcut。",
      tags: ["visual UI", "launcher", "handoff"]
    },
    {
      title: "手機與側邊欄是工作流入口，不是真相源",
      text: "Telegram/Chrome Extension 負責召喚與交付；GitHub repo、runtime DB、Google Sheets 才保存可追溯事實。",
      tags: ["telegram", "chrome", "source of truth"]
    }
  ],
  approval: [
    ["MAPLAB 客戶訊息", "A7 產草稿，Owner/Mina 核准後才能對外送出。"],
    ["MAPLAB 報價 / Sheet", "接口可以讀與產草稿；改 Sheet、改 GAS、正式報價單需明確批准。"],
    ["Investment OS", "不下單、不改券商、不建立未授權模擬單；只做研究、風控、缺資料與下一步。"],
    ["跨專案記憶", "角色變更要寫回 repo 文件與 extension module，不只留在聊天裡。"]
  ],
  entrypoints: [
    {
      name: "MAPLAB Handbook",
      path: "/Users/pagemacmini/maplab-ai-handbook",
      links: [
        ["CURRENT_STATUS", "../CURRENT_STATUS.md"],
        ["pitfalls", "../pitfalls.md"],
        ["AGENT_RULES", "../AGENT_RULES.md"],
        ["A6 LINE path", "../projects/line-quote-assistant.md"]
      ]
    },
    {
      name: "Investment OS",
      path: "/Users/pagemacmini/Documents/New project",
      links: [
        ["Local folder", "file:///Users/pagemacmini/Documents/New%20project/"],
        ["Runtime dashboard", "http://127.0.0.1:18501/"],
        ["B1 canonical bridge", "../projects/b1-investment-os-owner-persona-canonical.md"],
        ["B1 owner profile", "../projects/b1-investment-os-owner-profile.md"]
      ]
    }
  ],
  next: [
    {
      title: "P0: A6 runtime status block",
      body: "把最近 Telegram route、primary engine、fallback reason、Owner/Mina delivery 狀態輸出成 JSON，讓 panel 可讀。"
    },
    {
      title: "P0: Investment OS PM brief block",
      body: "把今日研究任務、資料 freshness、缺資料、下一步與 approval needed 做成 panel 區塊。"
    },
    {
      title: "P1: Memory editor",
      body: "只編輯 repo 中可審核的 persona/profile/pitfall 文件，不讓 agent 直接改不可見記憶。"
    },
    {
      title: "P1: Scheduled digest",
      body: "用 heartbeat/automation 或 launchd 產生 Owner-visible digest，重點是手機看得到而不是背景有跑。"
    },
    {
      title: "P1: Hermes runtime target sync",
      body: "Chrome Extension 已有 Hermes selector；下一步重建 task modules，讓各角色 JSON 也正式列入 Hermes cold-path target。"
    }
  ]
};

async function readJson(path, fallback) {
  if (window.location.protocol === "file:") return fallback;
  try {
    const res = await fetch(path, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to load ${path}`);
    return res.json();
  } catch (err) {
    console.warn(err);
    return fallback;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderTags(items) {
  return `<div class="tag-row">${(items || []).map((x) => `<span class="tag">${escapeHtml(x)}</span>`).join("")}</div>`;
}

function renderLinks(links) {
  return `<div class="link-list">${(links || []).map(([label, href]) => `
    <a href="${escapeHtml(href)}">
      <span>${escapeHtml(label)}</span>
      <span class="tiny">${escapeHtml(href)}</span>
    </a>
  `).join("")}</div>`;
}

function renderLaunchers(launchers) {
  const root = document.getElementById("launchers");
  root.innerHTML = launchers.map((item) => `
    <div>
      <div class="tiny">${escapeHtml(item.label)}</div>
      <div class="cmd">
        <code>${escapeHtml(item.command)}</code>
        <button type="button" data-copy="${escapeHtml(item.command)}">Copy</button>
      </div>
    </div>
  `).join("");
}

function renderSurfaces(items) {
  const root = document.getElementById("surfaces");
  root.innerHTML = items.map((item) => `
    <article class="item">
      <div class="item-title">
        <strong>${escapeHtml(item.name)}</strong>
        <span class="pill strong">${escapeHtml(item.status)}</span>
      </div>
      <p class="muted">${escapeHtml(item.body)}</p>
      ${renderLinks(item.links)}
    </article>
  `).join("");
}

function renderTakeaways(items) {
  const root = document.getElementById("takeaways");
  root.innerHTML = items.map((item) => `
    <article class="item">
      <h3>${escapeHtml(item.title)}</h3>
      <p class="muted">${escapeHtml(item.text)}</p>
      ${renderTags(item.tags)}
    </article>
  `).join("");
  root.insertAdjacentHTML("beforeend", `
    <div class="callout muted">
      來源：Owner 提供 BNext / KOC 文章；另外以 OpenAI Codex 官方說明核對 thread、project、steering、tools、memory/automation 等方向。
    </div>
  `);
}

function renderRoles(roles) {
  const root = document.getElementById("roles");
  root.innerHTML = roles.map((role) => `
    <article class="item">
      <div class="item-title">
        <strong>${escapeHtml(role.role_id)} — ${escapeHtml(role.name)}</strong>
      </div>
      <p class="muted">${escapeHtml(role.purpose)}</p>
      ${renderTags(role.capabilities)}
      <p class="tiny">Runtimes: ${(role.preferred_runtimes || []).map((x) => `<code>${escapeHtml(x)}</code>`).join(" ")}</p>
    </article>
  `).join("");
}

function renderPipelines(pipelines) {
  const root = document.getElementById("pipelines");
  root.innerHTML = pipelines.map((p) => `
    <article class="item">
      <h3>${escapeHtml(p.pipeline_id)} — ${escapeHtml(p.name)}</h3>
      <ol>${(p.steps || []).map((s) => `
        <li><code>${escapeHtml(s.id)}</code> <span class="tiny">${escapeHtml(s.input_type)} -> ${escapeHtml(s.output_type)}</span></li>
      `).join("")}</ol>
    </article>
  `).join("");
}

function renderApproval(items) {
  const root = document.getElementById("approval");
  root.innerHTML = items.map(([title, body]) => `
    <article class="item">
      <h3>${escapeHtml(title)}</h3>
      <p class="muted">${escapeHtml(body)}</p>
    </article>
  `).join("");
}

function renderEntrypoints(items) {
  const root = document.getElementById("entrypoints");
  root.innerHTML = items.map((item) => `
    <article class="item">
      <div class="plain-row">
        <strong>${escapeHtml(item.name)}</strong>
        <span class="tiny">${escapeHtml(item.path)}</span>
      </div>
      ${renderLinks(item.links)}
    </article>
  `).join("");
}

function renderNext(items) {
  const root = document.getElementById("next");
  root.innerHTML = `<div class="timeline">${items.map((item) => `
    <div class="timeline-row">
      <strong>${escapeHtml(item.title)}</strong>
      <span class="muted">${escapeHtml(item.body)}</span>
    </div>
  `).join("")}</div>`;
}

function bindCopyButtons() {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.getAttribute("data-copy");
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = "Copied";
        setTimeout(() => { button.textContent = "Copy"; }, 1200);
      } catch {
        window.prompt("Copy command", text);
      }
    });
  });
}

async function boot() {
  const [rolesCfg, taskCfg] = await Promise.all([
    readJson("./config/roles.json", { roles: FALLBACK_DATA.roles }),
    readJson("./config/task_templates.json", { pipelines: FALLBACK_DATA.pipelines })
  ]);

  renderLaunchers(PANEL_DATA.launchers);
  renderSurfaces(PANEL_DATA.surfaces);
  renderTakeaways(PANEL_DATA.takeaways);
  renderRoles(rolesCfg.roles || FALLBACK_DATA.roles);
  renderPipelines(taskCfg.pipelines || FALLBACK_DATA.pipelines);
  renderApproval(PANEL_DATA.approval);
  renderEntrypoints(PANEL_DATA.entrypoints);
  renderNext(PANEL_DATA.next);
  bindCopyButtons();
}

boot();
