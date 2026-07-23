# Implementation Plan

1. Audit MAPLAB role dispatch, Investment OS runtime, and live WordPress in
   three independent child sessions.
2. Build a narrow WordPress plugin with server-side administrator auth,
   no-store/noindex headers, private REST snapshot routes, and a read-only
   dashboard.
3. Build a local exporter that reads only non-secret launchctl and artifact
   freshness evidence.
4. Separate role summonability from task-module context freshness.
5. Add IOS strategy roles and a dedicated IOS-ALPHA product card.
6. Validate unit tests, anonymous HTTP behavior, logged-in UI, and a durable
   screenshot/review bundle.

## Migration rule

Move owner-facing readouts and freshness to WordPress. Keep data collection,
analysis, runtime databases, Telegram routing, and all broker-adjacent work on
the Mac. Failed or stale producers stay visibly degraded rather than serving
old output as current.
