# Navigators — Acceptance Criteria

Each item maps to one or more requirement IDs in `docs/REQUIREMENTS.md`.
An item may only be checked `[x]` when:

1. The corresponding code exists in the repository (not a stub),
2. An automated test exercises it,
3. The test passes on a real run (not a hand-typed number),
4. The evidence column below links to the test name/output/log/benchmark file.

No item may be checked from memory or intention. This file is the
ground truth for "is the project done" — it should always be checkable by
someone who has never seen the code.

| # | Criterion | Req ID(s) | Status | Evidence |
|---|-----------|-----------|--------|----------|
| 1 | Android reads real IMU | REQ-001 | ☐ Not started | |
| 2 | Android reads real GNSS | REQ-002 | ☐ Not started | |
| 3 | Sessions are recorded (with full metadata, no data loss offline) | REQ-005, REQ-006 | ☐ Not started | |
| 4 | Phone-to-vehicle alignment works | REQ-010, REQ-011 | ☐ Not started | |
| 5 | IMU calibration works | REQ-012, REQ-013 | ☐ Not started | |
| 6 | AI speed model performs real on-device inference | REQ-030, REQ-031 | ☐ Not started | |
| 7 | Navigation continues without GNSS | REQ-051 | ☐ Not started | |
| 8 | GNSS+INS fusion works | REQ-040, REQ-041, REQ-042 | ☐ Not started | |
| 9 | NHC works (and is correctly gated) | REQ-060 | ☐ Not started | |
| 10 | Map matching works offline | REQ-070 | ☐ Not started | |
| 11 | GNSS recovery works (controlled, logged) | REQ-052 | ☐ Not started | |
| 12 | External IMU interface works (≥2 real adapters) | REQ-080 | ☐ Not started | |
| 13 | IO-VNBD replay works | REQ-081 | ☐ Not started | |
| 14 | GNSS blackout simulation works (deterministic) | REQ-082 | ☐ Not started | |
| 15 | Evaluation metrics are automatically generated | REQ-100 | ☐ Not started | |
| 16 | Dashboard displays actual data (no fabricated values) | REQ-092 | ☐ Not started | |
| 17 | Offline data is retained (no loss on disconnect) | REQ-006 | ☐ Not started | |
| 18 | Reconnection synchronization works (idempotent, no dupes) | REQ-091 | ☐ Not started | |
| 19 | Model registry works (states + rollback) | REQ-093 | ☐ Not started | |
| 20 | Training runs are logged (experiment tracking) | REQ-030 (extended) | ☐ Not started | |
| 21 | Tests pass (CI green) | all | ☐ Not started | |
| 22 | Documentation is complete | — | ☐ Not started | |
| 23 | Drift benchmark is measured (report PASS/FAIL honestly vs <10%) | REQ-101 | ☐ Not started | |
| 24 | Smartphone output operates at ≥10 Hz | REQ-003, REQ-114 | ☐ Not started | |
| 25 | Edge engine is benchmarked near ~200 Hz | REQ-083 | ☐ Not started | |

## Reporting convention (used at the end of every phase)

```
PHASE STATUS
Implemented:
Tested:
Passed:
Failed:
Known Issues:
Evidence:
Next Phase:
```

A phase is never marked complete while any of its tests are failing. If a
number can't be backed by a script + log, it does not go in this document
or in any demo material.
