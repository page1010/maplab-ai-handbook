# Quote Pairing Report

- Run timestamp: `2026-06-30T09:03:38+08:00`
- Total candidates: `6929`
- High confidence 70+: `88`
- Medium confidence 30-70: `6841`
- Quote coverage: `95.6%`

## Inventory

| Source | Count |
|---|---:|
| LINE CSVs | 3625 |
| 2024 quote xlsx | 273 |
| 2025 quote xlsx | 61 |
| 2026 quote gsheet | 28 |
| 2026 photo folders | 12 |

## Candidate Policy

- Confidence scoring follows the requested point system.
- Kept candidates must also have at least one LINE-side anchor beyond date: matching headcount or payment/deal signal.
- This conservative anchor gate prevents date-only false positives because LINE display names do not equal quote-sheet client names.
- LINE conversations with takeout/self-pickup signals are excluded from catering quote pairing.
- Scored pairs in date window: `40133`
- Discarded below threshold: `32683`
- Discarded by anchor gate: `521`
- Excluded takeout conversations: `105`

## Ground Truth Validation

| ID | Status | Matched quote | Confidence | Reason |
|---|---|---|---:|---|
| QA-1 | not_found |  |  | quote file not found for expected date/headcount |
| QA-2 | not_found |  |  | quote file not found for expected date/headcount |
| QA-3 | not_found |  |  | quote file not found for expected date/headcount |
| QA-4 | correctly_excluded |  |  | no kept candidates for matched LINE contact |
| QA-5 | not_found |  |  | quote file not found for expected date/headcount |
| QA-6 | not_found |  |  | quote file not found for expected date/headcount |
| QA-7 | correctly_excluded |  |  | no LINE filename contact match found; no candidates produced |

## Top Candidates

| Confidence | Contact | LINE end | Quote date | Headcount | Quote | Reasons |
|---:|---|---|---|---:|---|---|
| 80 | 外** | 2024-02-08 | 2024-02-08 | 20 | 2024_2_8 1500_20人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-02-18 | 2024-02-18 | 11 | 2024_2_18 900_11人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-02-23 | 2024-02-23 | 13 | 2024_2_23 1100A_13人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-02 | 2024-03-02 | 15 | 2024_3_2 1300_1000 15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-03 | 2024-03-03 | 20 | 2024_3_3 800開幕_20人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-16 | 2024-03-16 | 25 | 2024_3_16 1100_25人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-16 | 2024-03-16 | 15 | 2024_3_16 1000A_15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-16 | 2024-03-16 | 25 | 2024_3_16 1100_25人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-17 | 2024-03-17 | 25 | 2024_3_17 1000_25人_ | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-17 | 2024-03-17 | 20 | 2024_3_17 700_20人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-17 | 2024-03-17 | 20 | 2024_3_17 800_20人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-03-30 | 2024-03-30 | 20 | 2024_3_30 1000_20人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-04-06 | 2024-04-06 | 30 | 2024_4_6 1300_30人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-04-06 | 2024-04-06 | 25 | 2024_4_6 700_25人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-04-06 | 2024-04-06 | 30 | 2024_4_6 800_30人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-04-21 | 2024-04-21 | 15 | 2024_4_21 700_15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-04 | 2024-05-04 | 15 | 2024_5_4 800_15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-04 | 2024-05-04 | 15 | 2024_5_4 800_15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-05 | 2024-05-05 | 15 | 2024_5_5 700_1200A 15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-11 | 2024-05-11 | 14 | 2024_5_11 1300_14人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-12 | 2024-05-12 | 30 | 2024_5_12 800_30人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-18 | 2024-05-18 | 30 | 2024_5_18 1000_30人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-18 | 2024-05-18 | 23 | 2024_5_18開幕900_23人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-19 | 2024-05-19 | 20 | 2024_5_19 700_20人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-05-25 | 2024-05-25 | 15 | 2024_5_25 900_15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-06-09 | 2024-06-09 | 15 | 2024_6_9 1000A_15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-06-09 | 2024-06-09 | 15 | 2024_6_9 800_15人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 洽** | 2024-06-15 | 2024-06-15 | 11 | 2024_6_15 1100_11人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-06-15 | 2024-06-15 | 35 | 2024_6_15 1000_35人 | date_match_exact,headcount_match,line_deal_signal |
| 80 | 外** | 2024-06-15 | 2024-06-15 | 25 | 2024_6_15 800_25人 | date_match_exact,headcount_match,line_deal_signal |

## Blocker

confirmed_pair_missed: QA-1=quote file not found for expected date/headcount; QA-2=quote file not found for expected date/headcount
