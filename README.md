# Navigators

AI/ML Intelligent Dead Reckoning & GNSS+INS Navigation System

## Current status: Phase 0 (scaffold only)

This repository currently contains **no working navigation code**. It
contains the repo skeleton and the three Phase 0 planning documents that,
per the project's working method, must exist before implementation starts:

- [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) — every requirement, broken
  into IDs, mapped to a component and a planned test.
- [`docs/ACCEPTANCE_CRITERIA.md`](docs/ACCEPTANCE_CRITERIA.md) — the binary
  checklist that defines "done"; every box is currently unchecked.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design, technology
  choices with justification, and Mermaid diagrams for every major data
  flow.

Every subdirectory has its own `README.md` stating its purpose and current
`NOT IMPLEMENTED` status, and which phase is expected to populate it.

## Why nothing is implemented yet

The project's own engineering rules (see the master prompt) require:
avoid fake/simulated functionality, validate the classical navigation
baseline before adding AI, and never report a benchmark number that wasn't
produced by an actual evaluation run. Phase 1 (IO-VNBD ingestion, timestamp
sync, replay engine, GNSS blackout simulator) is the next concrete step —
it builds the objective test bench that every later claim will be measured
against.

## Phased plan (see `docs/ARCHITECTURE.md` and `docs/REQUIREMENTS.md` for detail)

0. Requirements, architecture, traceability matrix — **this commit**
1. Data & replay: IO-VNBD ingestion, GNSS blackout simulator, replay engine
2. Classical navigation baseline: coordinate frames, quaternions, alignment,
   strapdown INS, ESKF GNSS fusion
3. Constraints: stationary detection, ZUPT, NHC
4. ML speed model: data pipeline, candidate architectures, benchmarking, export
5. AI-assisted fusion, benchmarked against the classical baseline
6. Offline map matching
7. Android integration
8. Backend (API, DB, sync, model registry)
9. Dashboard
10. Edge engine (external IMU, ~200Hz)
11. System integration testing
12. Benchmarking against IO-VNBD (drift < 10% target)
13. Demo hardening

## Working method

Each phase: inspect → define requirements → design → implement → run → test
→ fix → re-test → document → commit. A phase is not marked complete while
its tests are failing. See the `PHASE STATUS` reporting format in
`docs/ACCEPTANCE_CRITERIA.md`.
