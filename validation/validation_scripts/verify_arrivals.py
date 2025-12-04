# verify_arrivals.py
import os
import pandas as pd
import matplotlib.pyplot as plt

def verify_arrivals(metrics_df, outdir):
    arrivals = metrics_df[metrics_df['metric'] == "auth_latency"]
    if arrivals.empty:
        return {"num_players": 0}

    num_players = len(arrivals)
    print(f"[ARRIVALS] Total players authenticated: {num_players}")

    # Plot histogram of auth_latency
    plt.figure(figsize=(8,5))
    plt.hist(arrivals['value'], bins=40, alpha=0.7)
    plt.title("Player Authentication Latency")
    plt.xlabel("Latency (s)")
    plt.ylabel("Count")
    plt.tight_layout()
    path = os.path.join(outdir, "auth_latency.png")
    plt.savefig(path)
    plt.close()
    print(f"[ARRIVALS] Saved plot: {path}")

    return {"num_players": num_players}
