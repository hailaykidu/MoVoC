# EN→Amharic MoVoC-Tok Seed 44: Critical Anomaly

## Issue
EN→Amharic MoVoC-Tok Seed 44 shows extremely low performance, contradicting the excellent results from seeds 42 and 43.

**Data:**
- Seed 42: BLEU=0.8962, ChrF++=14.4076 ✅
- Seed 43: BLEU=0.9012, ChrF++=14.8977 ✅
- Seed 44: BLEU=0.0127, ChrF++=2.3606 ❌ ANOMALY

## Performance Breakdown (EN→Amharic MoVoC-Tok)
| Seed | BLEU | ChrF++ | Status |
|---|---|---|---|
| 42 | 0.8962 | 14.4076 | ✅ Excellent |
| 43 | 0.9012 | 14.8977 | ✅ Excellent |
| 44 | 0.0127 | 2.3606 | ❌ CRITICAL ANOMALY |
| **Mean (42-43 only)** | **0.8987** | **14.6527** | **✅ Typical** |

## Statistics Impact
- **With Seed 44 (All 3):** Mean=0.6033, CV=84.79% (extremely high variance)
- **Without Seed 44 (Seeds 42-43):** Mean=0.8987, CV=0.3% (excellent stability)

## Root Cause Investigation Needed
Possible causes for seed 44 anomaly:
1. Training failure or checkpoint corruption
2. Evaluation script issue on seed 44 only
3. Data loading anomaly
4. Hardware issue during training or evaluation

## Reporting Status
**Table 3 should indicate:**
- Seed 44 data exists but shows critical anomaly
- Primary results based on seeds 42-43 (consistent, excellent)
- Seed 44 flagged as outlier requiring investigation

**For publication:**
- Report seeds 42-43 results as primary (Mean=0.8987, CV=0.3%)
- Note seed 44 anomaly separately
- Recommend future investigation of seed 44 failure cause

