# Navigators Navigation Engine Benchmark Report
**Date:** 2026-09-12T11:43:19.622861

## Executive Summary
This report evaluates the performance of the Navigators navigation engine during simulated GNSS outages.

## Test Configuration
- **Outage Duration:** 30 seconds

## Ablation Results
| Configuration | Absolute Drift (m) | Drift % | Position RMSE (m) | Max Error (m) |
|---|---|---|---|---|
| B. Pure INS | 0.00 | 0.00% | 0.00 | 0.00 |
| C. INS + NHC | 0.00 | 0.00% | 0.00 | 0.00 |
| D. INS + NHC + AI | 0.00 | 0.00% | 0.00 | 0.00 |
| E. INS + NHC + AI + Map | 0.00 | 0.00% | 0.00 | 0.00 |

## Trajectory Plots
![Trajectory Comparison](trajectory_comparison.png)

## Error Plots
![Drift Curves](drift_curves.png)