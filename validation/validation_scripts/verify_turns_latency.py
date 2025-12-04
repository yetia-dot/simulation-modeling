# verify_turns_latency.py
import os
import pandas as pd
import matplotlib.pyplot as plt

def verify_turns_latency(metrics_df, outdir):
    d = metrics_df[metrics_df['metric'] == 'turn_latency']
    if d.empty:
        return {"mean": 0, "p95": 0}

    mean_latency = d['value'].mean()
    p95_latency = d['value'].quantile(0.95)

    print(f"[TURN LATENCY] Mean: {mean_latency:.3f}, 95th percentile: {p95_latency:.3f}")

    # Plot histogram
    plt.figure(figsize=(8,5))
    plt.hist(d['value'], bins=40, alpha=0.7)
    plt.title("Turn Latency Distribution")
    plt.xlabel("Latency (s)")
    plt.ylabel("Count")
    plt.tight_layout()
    path = os.path.join(outdir, "turn_latency.png")
    plt.savefig(path)
    plt.close()
    print(f"[TURN LATENCY] Saved plot: {path}")

    return {"mean": mean_latency, "p95": p95_latency}
