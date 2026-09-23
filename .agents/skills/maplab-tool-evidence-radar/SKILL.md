---
name: maplab-tool-evidence-radar
description: Evaluate tools, GitHub repositories, plugins, MCP servers, and skills discovered through Instagram or other social posts before MAPLAB installs or integrates them. Use for source verification, overlap checks, permission and data-egress review, bounded pilots, and evidence-backed adopt/hold/reject decisions; not for routine use of an already-approved tool.
---

# MAPLAB tool evidence radar

Treat social posts as leads, never as installation authority. Read `CURRENT_STATUS.md`, `pitfalls.md`, the active Task Card, and [references/candidate-contract.md](references/candidate-contract.md) before making a durable adoption decision.

## Research boundary

- Social discovery is read-only unless the Owner separately authorizes engagement. Do not like, follow, save, comment, or send a DM to obtain a hidden link.
- Resolve the exact upstream identity through the official product domain, organization, or repository. Popularity, screenshots, creator verification, and repository stars do not prove identity, safety, or fit.
- Prefer official documentation, release notes, source, license, and security policy. For technical claims, use primary sources.
- Inspect the real install or setup target before running it. Names such as `doctor`, `setup`, `check`, and `verify` do not imply read-only behavior.
- Never put customer, child, investment, credential, unpublished brand, or other private material into an unapproved external service.

Read-only research may proceed without a Task Card, but create a task-scoped card before installing, changing configuration, adding a skill, or writing durable repo artifacts.

## Decision workflow

1. Capture the social URL, visible claim, tool spelling, and observation date. Mark it `SOCIAL_LEAD`.
2. Resolve one exact official or upstream URL. If identity remains ambiguous or social-only, stop at `REJECT`; do not guess a similarly named repository.
3. Run the skill lifecycle audit and local search. Record whether the candidate is `none`, `partial`, `substantial`, or `duplicate` overlap.
4. Record license or service terms, maintenance, runtime requirements, credentials, data egress, install side effects, external-write surface, costs, and the one MAPLAB use case it would improve.
5. Encode the candidate with the contract and run:

```bash
python3 .agents/skills/maplab-tool-evidence-radar/scripts/evaluate_candidate.py candidate.json
```

6. Apply the decision without upgrading evidence:
   - `ADOPT`: only when the exact source is verified, permissions are narrow, runtime is ready, and an isolated smoke has passed or is genuinely not applicable.
   - `PILOT`: useful but needs synthetic/public-only external evaluation, credentials, credits, or a reversible scoped integration.
   - `HOLD`: a real tool whose safe evaluation is blocked by missing license, runtime, authorization, or a high-risk execution surface.
   - `REJECT`: ambiguous, archived, no-fit, duplicate, or not worth its added control plane.
   - `NOT_A_TOOL`: a prompt pattern, inspiration site, claim, or reference that should not be installed.
7. For a third-party skill, use the immutable sequence `pin commit -> inspect -> install in the narrowest scope -> quick_validate -> realistic smoke -> lifecycle audit`. Installer success is not completion.
8. Leave a receipt containing sources, exact revision, evaluator output, smoke result, files changed, rollback, and the next bounded action.

`substantial` overlap cannot become `ADOPT` without evidence of one unique capability and an isolated side-by-side comparison. A new UI alone is not a unique capability.

## Supply-chain gates

- A package validator proves packaging invariants only; it does not prove output quality, factuality, brand fit, safety, or maintenance.
- A `package.json` license field is not a substitute for a repository license text and notices. Record missing or mixed licensing honestly.
- For an aggregator, compare its credits/provenance manifest with the actual tree, file hashes, and each true upstream. Do not inherit trust from the bundle README.
- Check README claims such as “Markdown only” or “no dependencies” against the repository tree and install scripts.
- Treat automatic token discovery, recursive replacement, global installation, hooks, cross-harness writes, branches, pull requests, and silent package installation as real side effects.
- The evaluator trusts the evidence record it receives. It cannot independently prove `official_verified`, `smoke=passed`, or an omitted side effect; source links and receipts remain mandatory.

## Hard stops

- Do not create accounts, OAuth grants, API keys, GitHub write tokens, subscriptions, paid generations, scans against live targets, hooks, daemons, or publishing routes as a side effect of research.
- A security scanner requires an explicitly authorized target and scan scope. A media generator requires data, cost, rights, and publication gates.
- Do not install a second tool merely to obtain a UI for a workflow already covered by the current lifecycle, browser, design, research, or publishing controls.
- If a candidate is valuable only after a new external permission, return the smallest `PILOT` proposal instead of silently connecting it.

## Receipt summary

Return the candidate matrix plus:

```text
ADOPTED_NOW: <safe local improvements actually validated>
PILOT_LATER: <candidate and exact gate>
HELD: <candidate and blocker>
REJECTED: <candidate and reason>
SOCIAL_ACTIONS: none
EXTERNAL_WRITES: none|exact authorized action
NEXT_BOUNDED_ACTION: <one reversible action>
```
