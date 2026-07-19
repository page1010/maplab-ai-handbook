# First-cycle curriculum inventory

| Curriculum | Fixed cases | Source mode | Baseline target | Main safety boundary |
|---|---:|---|---|---|
| Investment report/current state | 20 | Synthetic, de-identified, broker-free | `qwen2.5:14b` | Entity/date/provenance/simulation/order separation |
| SEO ranking/keyword | 20 | Synthetic, de-identified, read-only | `qwen2.5:14b` | Live evidence versus strategy/stale/wrong-locale/write actions |

No teacher output or Google Drive row was admitted to a training dataset.
Drive/Sheets was used only to confirm data-domain topology and narrow headers:

- MAPLAB main Sheet contains private customer/message surfaces that are excluded.
- A6 training sheet explicitly uses de-identified message/reply fields.
- A2 matrix contains keyword/Ads/UTM strategy columns, but no current GSC rank
  and observation timestamp; it is not ranking truth.
- Investment OS Drive folders were inspected at metadata level only.

The eval manifest is frozen at 40 cases for the cycle. Any future case addition
must receive a new eval version; it cannot silently change these baseline scores.
