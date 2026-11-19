# GTA VI Trophy Rarity Forecast (NUR)

[![Bounty](https://make.fun/badge/gta6-trophy-rarity-forecast-01.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01)
[![Rank](https://make.fun/badge/gta6-trophy-rarity-forecast-01/Sipalingtesnet/gta6-trophy-rarity-forecast-01-nur/rank.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01)
[![Reward](https://make.fun/badge/gta6-trophy-rarity-forecast-01/Sipalingtesnet/gta6-trophy-rarity-forecast-01-nur/reward.svg)](https://make.fun/bounty/gta6-trophy-rarity-forecast-01)

Forecasting Grand Theft Auto VI player trophy acquisition rates for week one.

## Approach
Our model fits per-trophy logit-transformed earn rates against $\ln(1 + \text{hours since launch})$ using historical Exophase snapshots. Slopes are regularized via cross-trophy median shrinkage to ensure robust extrapolation. Prediction intervals combine trend residual variance with a random-walk growth component, mapped back through the logistic function to generate calibrated non-decreasing quantile distributions.

## Local Execution
```bash
mkdir -p out
MAKEFUN_INPUT_DIR=kit/input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Competition details: [make.fun/bounty/gta6-trophy-rarity-forecast-01](https://make.fun/bounty/gta6-trophy-rarity-forecast-01).
