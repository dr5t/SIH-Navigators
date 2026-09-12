# Navigators — Requirements & Traceability Matrix

**SIH Problem Statement:** SIH26168 — AI/ML based intelligent dead reckoning
mechanism for GNSS-denied navigation, using smartphone IMU + GNSS only (no
OBD-II / CAN / wheel-speed dependency).

**Status of this document:** Phase 0 draft. Requirements below are derived
from the master engineering prompt. They have **not yet been implemented**;
the "Component" and "Test" columns name the intended home for each piece of
work, not code that currently exists. This document is the single source of
truth for what "done" means — every later phase should update the
`Implementation` and `Evidence` columns with real artifacts (file paths,
commit hashes, test names, benchmark numbers), never with prose claims.

Requirement IDs are stable — do not renumber once implementation begins.

---

## 1. Sensor Acquisition & Recording

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-001 | Capture accelerometer (ax,ay,az), gyroscope (gx,gy,gz), magnetometer (mx,my,mz) with high-resolution monotonic timestamps | `android/` sensor layer | Unit test: timestamp monotonicity, no dropped-sample silent failure | Not started | — |
| REQ-002 | Capture GNSS lat/lon/alt/speed/bearing/h-accuracy/v-accuracy/satellite info/timestamp | `android/` GNSS layer | Integration test against mock LocationManager | Not started | — |
| REQ-003 | IMU sampling target 100–200 Hz where hardware permits; GNSS at device-supported rate; nav output ≥10 Hz | `android/`, `navigation-core/` | Performance test measuring achieved loop rate | Not started | — |
| REQ-004 | Timestamp synchronization/interpolation between async accel/gyro streams | `navigation-core/filtering` | Unit test with synthetic offset streams | Not started | — |
| REQ-005 | Session recording with full metadata (session_id, device_id, start/end, sampling stats, calibration, model version, config) | `android/`, `backend/` | Schema validation test | Not started | — |
| REQ-006 | Raw sensor data stored locally; never lost on connectivity loss | `android/` local DB | Integration test: kill network mid-session, verify no data loss | Not started | — |

## 2. Alignment & Calibration

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-010 | Estimate phone-to-vehicle roll/pitch/yaw; phone→vehicle→navigation frame transforms | `navigation-core/alignment` | Unit test against synthetic rotated IMU data with known ground-truth rotation | Not started | — |
| REQ-011 | Recompute alignment when significant phone movement detected | `navigation-core/alignment` | Unit test triggering recalibration event | Not started | — |
| REQ-012 | Accelerometer/gyroscope bias, scale error, gravity magnitude calibration; stationary-triggered bias update | `navigation-core/calibration` | Unit test with known injected bias | Not started | — |
| REQ-013 | Store calibration parameters + confidence score | `navigation-core/calibration` | Persistence round-trip test | Not started | — |

## 3. Signal Processing & Motion Classification

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-020 | Configurable filtering (low/high/band-pass, Butterworth, median, Savitzky-Golay); cutoffs experimentally justified | `navigation-core/filtering` | Frequency-response unit test + documented cutoff derivation in `docs/NAVIGATION_MATH.md` | Not started | — |
| REQ-021 | Classify motion state: stationary/driving/accel/decel/turn/idle/pothole/speed-breaker/rough-road/phone-movement | `navigation-core/filtering` (or dedicated `motion/` module) | Labeled-segment classification accuracy test on IO-VNBD | Not started | — |

## 4. AI Speed Estimation

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-030 | Benchmark ≥3 candidate architectures (LSTM/GRU/1D-CNN/TCN/CNN-LSTM/Transformer-lite/physics-informed) on MAE, RMSE, latency, size, memory, CPU | `ml/models`, `ml/evaluation` | Automated benchmark script producing a results table | Not started | — |
| REQ-031 | Selected model exported to TFLite or ONNX Runtime Mobile, runs fully offline | `ml/export` | On-device (or emulator) inference test with no network | Not started | — |
| REQ-032 | Trajectory-based train/val/test split (no leakage) | `ml/preprocessing` | Unit test asserting no shared session/trajectory IDs across splits | Not started | — |

## 5. Strapdown INS & Fusion

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-040 | Quaternion-based orientation propagation, gravity compensation, specific-force integration, velocity/position propagation with variable timestep | `navigation-core/ins` | Unit test: static case (should output zero velocity drift beyond bias), known-trajectory replay | Not started | — |
| REQ-041 | Error-State EKF (or justified alternative) with documented state vector, process model, measurement model, covariance | `navigation-core/fusion` | Unit test against synthetic linear/circular trajectory with known noise | Not started | — |
| REQ-042 | GNSS corrects accumulated inertial error when available | `navigation-core/fusion` | Integration test comparing INS-only vs fused error growth | Not started | — |
| REQ-043 | AI-assisted fusion (adaptive covariance / bias correction / drift correction) shown to quantitatively beat classical baseline | `navigation-core/fusion`, `ml/` | A/B benchmark: classical ESKF vs AI-enhanced, same trajectories | Not started | — |

## 6. GNSS Outage Handling

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-050 | Multi-signal GNSS quality classification (accuracy, sat count, age, speed consistency, innovation residuals) into GNSS_FUSED / GNSS_DEGRADED / DEAD_RECKONING / GNSS_RECOVERY, with logged transitions | `navigation-core/fusion` | Unit test driving state machine through all transitions | Not started | — |
| REQ-051 | Navigation continues (does not freeze) during GNSS loss; uncertainty grows monotonically with outage duration | `navigation-core/fusion`, `navigation-core/ins` | Integration test on injected blackout, assert position keeps updating and covariance trace increases | Not started | — |
| REQ-052 | Controlled re-localization on GNSS recovery (no teleport); log outage duration, DR endpoint, recovery position, recovery error, correction magnitude | `navigation-core/fusion` | Integration test asserting bounded correction rate | Not started | — |

## 7. Constraints

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-060 | Non-holonomic constraint (lateral/vertical velocity ≈ 0) applied only when motion-state confidence is high | `navigation-core/constraints` | Unit test: NHC must not fire during detected turns/abnormal motion | Not started | — |
| REQ-061 | Zero-velocity update (ZUPT) when confidently stationary, with false-positive guard | `navigation-core/constraints` | Unit test with stationary and near-stationary synthetic segments | Not started | — |

## 8. Map Matching

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-070 | Offline OSM-derived road graph; HMM/Viterbi trajectory-aware candidate scoring (not nearest-snap) | `navigation-core/map_matching` | Unit test against a small synthetic road network with known correct path | Not started | — |
| REQ-071 | DR error measured with and without map matching to show contribution | `evaluation/` | Benchmark comparison | Not started | — |

## 9. External IMU / Edge / Replay

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-080 | Generic `ImuSource` interface; Android, CSV/dataset, external-serial adapters all implement it; `navigation-core` agnostic to source | `navigation-core/`, `edge/` | Interface conformance test run against all three adapters | Not started | — |
| REQ-081 | Replay engine reuses the live navigation pipeline; LIVE/REPLAY/SIMULATION modes, SIMULATION always visibly labeled | `replay/` | Integration test: replayed session produces identical output to a live run of same data | Not started | — |
| REQ-082 | Deterministic GNSS blackout injection (`--gnss-blackout-start`, `--gnss-blackout-duration`) with ground truth kept separate | `replay/`, `evaluation/` | Reproducibility test: same seed → identical blackout window and metrics | Not started | — |
| REQ-083 | Edge engine benchmarked near 200 Hz | `edge/` | Throughput benchmark script | Not started | — |

## 10. Backend, Sync, Dashboard, Registry

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-090 | Versioned REST API (`/api/v1/...`) with validation, structured errors, pagination, OpenAPI docs | `backend/` | API contract tests | Not started | — |
| REQ-091 | Offline-first sync: LOCAL_ONLY → QUEUED → SYNCING → SYNCED / FAILED; idempotent uploads, no duplicates | `android/`, `backend/` | Integration test: duplicate upload of same session_id | Not started | — |
| REQ-092 | Real-time dashboard (WebSocket/SSE) showing only real data; explicit OFFLINE/LAST SEEN state, never fake movement | `dashboard/`, `backend/` | Manual + automated test: disconnect device, verify dashboard freezes with correct status | Not started | — |
| REQ-093 | Model registry with EXPERIMENTAL/CANDIDATE/PRODUCTION/ARCHIVED states; mobile verifies compatibility before activation; rollback supported | `backend/`, `android/` | Integration test: deploy → verify → rollback | Not started | — |

## 11. Evaluation

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-100 | Automated computation of ATE, position/velocity RMSE & MAE, heading error, final displacement error, max error, 95th percentile error, drift % | `evaluation/` | Unit test against known synthetic trajectory with hand-computed expected metrics | Not started | — |
| REQ-101 | Primary requirement: drift < 10% (final_position_error / GNSS_denied_distance × 100) on IO-VNBD benchmark | `evaluation/` | End-to-end benchmark run, PASS/FAIL reported honestly | Not started | — |
| REQ-102 | Baseline ladder implemented and compared: Raw INS → Filtered+INS → INS+EKF → +NHC → +Map Matching → Final (AI speed + AI fusion + NHC + MM) | `evaluation/`, `navigation-core/` | Results table generated by benchmark script, not hand-written | Not started | — |

## 12. Cross-cutting (Testing, Security, Logging, Performance)

| ID | Requirement | Component | Test (planned) | Implementation | Evidence |
|----|-------------|-----------|------------------|-----------------|----------|
| REQ-110 | No secrets in source/APK/git history/JS; TLS in deployed environments | `backend/`, `android/`, CI | Secret-scan in CI | Not started | — |
| REQ-111 | Structured logging (timestamp, severity, component, session_id, device_id, event, message, metadata) | all components | Log schema unit test | Not started | — |
| REQ-112 | Observability: IMU rate, dropped samples, GNSS rate, nav-loop latency, inference latency, CPU/memory, sync queue size, API latency, WS status, DB health | `backend/`, `dashboard/` | Metrics-exposed integration test | Not started | — |
| REQ-113 | Graceful, non-silent failure handling for the 13 failure modes in the master prompt §49 | all components | Fault-injection tests per failure mode | Not started | — |
| REQ-114 | Navigation output ≥10 Hz on target hardware without blocking UI/network/DB | `android/`, `navigation-core/` | Profiling benchmark | Not started | — |

---

## Out of scope for this system (explicitly excluded per spec)

- OBD-II integration
- Wheel-speed sensor integration
- Vehicle CAN bus integration
- Dependency on any external vehicle computer

These may be accepted as *optional additional inputs* via the external IMU
interface (REQ-080) but the system must function fully without them.

## Next document

See `docs/ACCEPTANCE_CRITERIA.md` for the binary pass/fail checklist derived
from this matrix, and `docs/ARCHITECTURE.md` for the system design that
satisfies it.
