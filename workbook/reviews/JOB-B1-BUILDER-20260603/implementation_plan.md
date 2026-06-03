# Implementation Plan

Job: JOB-B1-BUILDER-20260603

Role: B1 Investment OS Builder

## Plan

1. Add MAPLAB project context for the Investment OS strategy role system.
2. Add a shared IOS role recall prompt for Chrome Extension task modules.
3. Extend the dynamic role module generator so IOS roles can share the recall
   while keeping role-specific startup contracts and output contracts.
4. Generate 16 IOS role modules and update the module index, relation graph,
   relationship CSV, and Extension config.
5. Update Chrome Extension popup grouping and auto-routing so Owner can summon
   strategy owners directly.

## Boundary

The Extension loads JSON/Markdown routing data only. It does not execute remote
code and does not replace Investment OS local truth sources.
