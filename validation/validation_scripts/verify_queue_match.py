# verify_queue_match.py
import os
import pandas as pd
import matplotlib.pyplot as plt

def verify_queue_match(metrics_df, outdir):
    # Queue Length Analysis
    q = metrics_df[metrics_df['metric'] == 'queue_length']['value']
    queue_max = q.max() if not q.empty else 0
    queue_mean = q.mean() if not q.empty else 0

    print(f"[QUEUE] Max: {queue_max}, Mean: {queue_mean}")

    # Plot queue length over time
    d = metrics_df[metrics_df['metric'] == 'queue_length']
    if not d.empty:
        plt.figure(figsize=(10,5))
        plt.plot(d['timestamp'], d['value'], label='Queue Length')
        plt.title("Queue Length Over Time")
        plt.xlabel("Time")
        plt.ylabel("Queue Length")
        plt.tight_layout()
        path = os.path.join(outdir, "queue_length.png")
        plt.savefig(path)
        plt.close()
        print(f"[QUEUE] Saved plot: {path}")

    # Match creation analysis
    matches = metrics_df[metrics_df['metric'] == 'matches_created']
    if not matches.empty:
        plt.figure(figsize=(8,5))
        plt.hist(matches['value'], bins=20, alpha=0.7)
        plt.title("Number of Matches Created")
        plt.xlabel("Count")
        plt.ylabel("Frequency")
        path = os.path.join(outdir, "matches_created.png")
        plt.savefig(path)
        plt.close()
        print(f"[MATCH] Saved plot: {path}")

    return {"queue_max": queue_max, "queue_mean": queue_mean, "matches_created": len(matches)}
