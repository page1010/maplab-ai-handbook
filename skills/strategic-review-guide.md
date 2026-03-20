# Strategic Review Guide (Big Picture Thinking)

Version: 1.0
Created: 2026-03-17
Purpose: Force agents to STOP and think holistically before diving into execution

## Core Principle

> Before writing a single line of code, UNDERSTAND the full landscape.
> 10 minutes of strategic thinking saves 10 hours of rework.

## When to Use This Skill

- Starting a new phase or project
- After completing a major milestone (pause before rushing forward)
- When context switches (new session, new agent takes over)
- When you feel the urge to "just start coding"
- When the dataset or scope is unclear

## The 5-Question Framework

### Q1: What do we ACTUALLY have?
- Inventory all data sources, files, folders
- Count and categorize (file types, sizes, formats)
- Identify anomalies (weird names, empty folders, duplicates)
- Run a discovery scan BEFORE planning

### Q2: What could go WRONG?
- List every failure mode you can think of
- Rate each: likelihood (H/M/L) x impact (H/M/L)
- Focus on H/H and H/M risks first
- Common risks: encoding issues, rate limits, storage limits, timeout, duplicates, corrupt files

### Q3: What should we SKIP or DEFER?
- Not everything needs processing
- Trash folders? Failed videos? Screenshots of receipts?
- Calculate: if we skip X, we save Y hours and Z API calls
- Create an exclusion list with justification

### Q4: What is the OPTIMAL order?
- Dependencies: what must happen before what?
- Quick wins: what gives 80% value with 20% effort?
- Batch strategy: how to group similar operations?
- Checkpoint strategy: where to save progress?

### Q5: What do we need from HUMANS?
- Decisions only humans can make (keep/delete, naming preferences)
- Access or permissions needed
- Budget approvals (API costs, storage)
- Collect ALL questions upfront, not one at a time

## MAPLAB Photo Pipeline Strategic Checklist

### Data Assessment
- [ ] Total file count by type (HEIC, JPG, PNG, MP4, MOV, JSON, etc.)
- [ ] Screenshot count and identification pattern
- [ ] Video count and total size
- [ ] JSON sidecar metadata: what EXIF data is already available?
- [ ] Duplicate detection: same file in multiple folders?
- [ ] Special folders identified and categorized (skip/process/ask user)

### Resource Estimation
- [ ] Gemini API calls needed = (total files - skippable) x retries
- [ ] Estimated API cost
- [ ] Estimated processing time (with rate limits)
- [ ] Storage needed: original + WebP + manifest files
- [ ] Current storage available vs needed

### Risk Register
- [ ] Storage overflow (current usage vs quota)
- [ ] API rate limiting (requests per minute/day)
- [ ] Colab timeout (max 12h, typically disconnects in 1-2h idle)
- [ ] Unicode/encoding in filenames
- [ ] HEIC format support (need conversion library)
- [ ] Network interruption mid-batch

### Decision Points for User
- [ ] Process trash folder contents? (Y/N)
- [ ] Process failed videos? (Y/N)
- [ ] Process screenshots separately? (Y/N)
- [ ] Naming convention preferences
- [ ] Category taxonomy approval
- [ ] Budget limit for API calls

## Output Format

After completing the strategic review, produce a brief report:

```
STRATEGIC REVIEW REPORT
Date: YYYY-MM-DD
Phase: [phase name]

DATA INVENTORY:
  Total files: X
  By type: HEIC(X), JPG(X), MP4(X), JSON(X)...
  Skippable: X files (reason)
  To process: X files

RISKS (top 3):
  1. [risk] - mitigation: [plan]
  2. [risk] - mitigation: [plan]
  3. [risk] - mitigation: [plan]

DECISIONS NEEDED:
  1. [question for user]
  2. [question for user]

RECOMMENDED ORDER:
  Step 1: ...
  Step 2: ...
```

## Anti-Patterns (DO NOT)

- DO NOT start coding without data inventory
- DO NOT assume file types from folder names
- DO NOT process everything (filter first)
- DO NOT ignore storage constraints
- DO NOT make user decisions for them
- DO NOT plan without checking current resource usage