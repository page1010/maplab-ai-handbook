# Local Control Plane (Model-Agnostic)

This folder is the persistent visual entrypoint for MAPLAB + Investment OS agent runtime work.

## Why this exists

Owner liked the HTML workbench pattern, but a one-off HTML file is easy to lose after closing it. This control plane fixes that by giving the panel a stable repo path, a double-click launcher, and a documented reopen command.

## Open the panel

Preferred:

```bash
/Users/pagemacmini/maplab-ai-handbook/open-agent-runtime-panel.command
```

Terminal:

```bash
/Users/pagemacmini/maplab-ai-handbook/scripts/open_agent_runtime_panel.sh open
```

Reveal in Finder:

```bash
/Users/pagemacmini/maplab-ai-handbook/scripts/open_agent_runtime_panel.sh reveal
```

The panel itself is:

- `local-control-plane/panel.html`

No build step is required. The panel has file-protocol fallback data, so it still renders when opened directly from Finder without a local server.

## What it shows

- Persistent surfaces: panel, Chrome Extension role recall, Telegram/A6.
- Continuous workflow takeaways: durable thread, external memory, verifiable goal, visual inspection.
- Agent profiles: A0/A1/A5/A6/A7/B1 plus Investment OS risk/left/right roles.
- Runtime pipelines: MAPLAB quote route, Investment OS research route, external-memory feedback loop.
- Approval gates: customer-facing MAPLAB actions and Investment OS trading boundaries.
- Project entrypoints: canonical MAPLAB repo and Investment OS folder/dashboard links.

## Data contracts

- `config/roles.json`: role capability matrix and runtime preferences.
- `config/task_templates.json`: task pipeline templates and output contracts.
- `config/verification_bundles.json`: verification checklist families.

## Integration rule

The panel is a visible surface, not the source of truth. The source of truth remains repo-tracked Markdown/JSON, runtime DBs, Google Sheets, and Git history. When runtime behavior changes, update the underlying contract first, then refresh the panel.
