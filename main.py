import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]

def clamp(x: float) -> float:
    return min(99.99, max(0.01, x))

def logit(pct: float) -> float:
    return math.log(clamp(pct) / (100 - clamp(pct)))

def logistic(lg: float) -> float:
    p = 1.0 / (1.0 + math.exp(-lg))
    return clamp(p * 100.0)

def round4(x: float) -> float | int:
    scaled = x * 10000
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 10000
    return int(value) if value.is_integer() else value

def parse_time(iso_str: str) -> float:
    try:
        from datetime import datetime, timezone
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        ref = datetime(2026, 11, 19, 0, 0, 0, tzinfo=timezone.utc)
        return (dt - ref).total_seconds() / 3600.0
    except Exception:
        return 0.0

def forecast_case(case: dict, name: str) -> dict:
    if case["levels"] != LEVELS:
        raise ValueError(f"{name} asks for levels {case['levels']}, not {LEVELS}")
    if not case["history"]:
        raise ValueError(f"{name} has no history")

    history = case["history"]
    trophies = case["trophies"]
    horizon_days = case["horizon_minutes"] / 1440.0
    target_time_str = case["target"]
    target_hours = parse_time(target_time_str)

    times = [parse_time(h["slot"]) for h in history]
    last_read = history[-1]
    
    rows = []
    slopes = []
    trophy_fits = []

    for i, trophy in enumerate(trophies):
        t_rates = []
        t_times = []
        for idx, h in enumerate(history):
            r = h["rates"][i]
            if r is not None:
                t_rates.append(r)
                t_times.append(times[idx])
        
        last_rate = last_read["rates"][i] if last_read["rates"][i] is not None else 1.0
        
        if len(t_rates) < 3:
            trophy_fits.append(None)
            continue

        xs = [math.log(1.0 + t) for t in t_times]
        ys = [logit(r) for r in t_rates]
        
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        
        num = sum((xs[j] - mean_x) * (ys[j] - mean_y) for j in range(n))
        den = sum((xs[j] - mean_x) ** 2 for j in range(n))
        
        if den > 1e-9:
            slope = num / den
            intercept = mean_y - slope * mean_x
            res_sq = sum((ys[j] - (slope * xs[j] + intercept)) ** 2 for j in range(n))
            res_std = math.sqrt(res_sq / max(1, n - 2))
        else:
            slope = 0.0
            intercept = mean_y
            res_std = 0.2

        slopes.append(slope)
        trophy_fits.append((slope, intercept, res_std, t_rates[-1]))

    median_slope = sorted(slopes)[len(slopes) // 2] if slopes else 0.0

    for i, trophy in enumerate(trophies):
        last_rate = last_read["rates"][i] if last_read["rates"][i] is not None else 1.0
        fit = trophy_fits[i]

        if fit is None:
            lg = logit(last_rate)
            spread = 0.5 * math.sqrt(horizon_days)
            qs = [logistic(lg + z * spread) for z in Z]
        else:
            slope, intercept, res_std, t_last_rate = fit
            shrunk_slope = 0.7 * slope + 0.3 * median_slope
            target_x = math.log(1.0 + target_hours)
            pred_lg = shrunk_slope * target_x + intercept
            
            last_lg = logit(t_last_rate)
            max_shift = 1.5 * math.sqrt(horizon_days + 0.1)
            pred_lg = max(last_lg - max_shift, min(last_lg + max_shift, pred_lg))

            spread = 0.5 * math.sqrt(horizon_days) + 0.5 * res_std
            qs = [logistic(pred_lg + z * spread) for z in Z]

        for j in range(1, len(qs)):
            if qs[j] < qs[j-1]:
                qs[j] = qs[j-1]

        rows.append({"id": trophy["id"], "q": [round4(q) for q in qs]})

    return {"trophies": rows}

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
