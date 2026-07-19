# Privacy, rights, and security review

## Passed boundaries

- No `.env`, credential, token, private key, or broker secret was read or copied.
- Provider health probes discarded stdout/stderr and stored only status/exit evidence.
- No OpenAI, Anthropic, or Gemini usage API was called.
- No real order, broker write, SEO publish, Ads/GSC mutation, customer reply, or
  formal quote was executed.
- Google Drive/Sheets reads were metadata and narrow header/schema checks only.
- All 40 eval cases are synthetic and de-identified.
- Training dataset admission remains zero; teacher dataset admission remains zero.
- No LoRA/adapter framework was installed and no model weights changed.
- No launchd/scheduler was installed or modified.

## Rights decision

Only synthetic fixtures, repo governance, and approved schema metadata are
eligible for this eval. Raw customer messages, phones, LINE ids, holdings,
account data, teacher outputs, and rights-unclear material remain excluded.

## Known hazards

1. `investment_os.db` exists but is empty while `investment_os.sqlite3` contains
   the live schema. Any future adapter must use an explicit canonical path.
2. Subscription CLI health does not expose remaining quota.
3. A2 strategy matrix is not current ranking evidence.
4. Candidate 100% is contract safety, not semantic model promotion.

## High-risk approvals still required

Paid API usage, teacher-job execution, data admission with unclear rights,
LoRA/adapter work, schedule installation, production writes, publishing,
customer communications, formal quotes, and any model promotion.
