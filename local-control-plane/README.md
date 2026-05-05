# Local Control Plane (Model-Agnostic)

This folder provides a local, model-agnostic control panel for MAPLAB agent orchestration.

## Goal
- Decouple role execution from a single model provider.
- Make task ownership, inputs, outputs, and status visible.
- Allow any compatible model runtime (Claude, Ollama, GPT, Gemini) to take over by contract.

## Run
Open this file in browser:

- `local-control-plane/panel.html`

No build step required.

## Data Contracts
- `config/roles.json`: role capability matrix and runtime preferences.
- `config/task_templates.json`: task decomposition templates and output contracts.

## Next Step Integration
1. Hook A6 bot dispatcher to read `roles.json` and route by capability.
2. Emit each run as a `run_log` JSON artifact.
3. Add verifier step to check output schema before publish.
