# Video evidence contract

Use this receipt shape for a MAPLAB video readback:

```text
status: EVIDENCE_READY | PARTIAL_EVIDENCE | BLOCKED_EGRESS
source: <URL or local path>
source_class: public | user_supplied | maplab_private | unknown
source_sha256: <hash for local input, otherwise n/a>
question: <bounded question>
range: <start-end or full>
tools: <ffprobe/watch version and options>
transcript_source: native_captions | approved_provider | none
egress: none | <approved provider and reason>
frames_reviewed: <count>
observations: <timestamped visible facts>
spoken_evidence: <timestamped transcript facts>
inferences: <explicitly labelled>
coverage_limit: <what was not inspected or cannot be proven>
work_dir: <exact retained directory>
next_action: <smallest follow-up>
```

Privacy routing:

| Source | Frames in Codex | Native captions | Cloud Whisper |
|---|---|---|---|
| public URL | allowed for the task | allowed | only if useful and disclosed |
| user-supplied local video | allowed for the task | allowed if embedded | explicit per-run authorization |
| MAPLAB/customer/child/private | only within approved task scope | local only | prohibited by default |
| unknown ownership | metadata only | no | no |

The receipt proves sampled analysis only. It never upgrades a render to `QA_PASS` and never authorizes publishing.
