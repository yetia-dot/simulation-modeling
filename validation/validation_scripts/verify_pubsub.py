# verify_pubsub.py
import os
import pandas as pd
import matplotlib.pyplot as plt

def verify_pubsub(metrics_df, outdir):
    pub = metrics_df[metrics_df['metric'].str.contains("pubsub")]
    if pub.empty:
        return {"total_delivered": 0, "total_retries": 0}

    delivered = pub[pub['metric'] == "pubsub_delivered"]['value'].sum()
    retries = pub[pub['metric'] == "pubsub_retry"]['value'].sum()

    print(f"[PUBSUB] Total delivered: {delivered}, Total retries: {retries}")

    # Plot retries over time
    retries_df = pub[pub['metric'] == "pubsub_retry"]
    if not retries_df.empty:
        # Group retries by timestamp to count occurrences
        retry_counts = retries_df.groupby('timestamp').size()

        # Plot retries counts over time
        plt.figure(figsize=(10,5))
        plt.bar(retry_counts.index, retry_counts.values, width=0.05, alpha=0.7)
        plt.title("PubSub Retries Over Time")
        plt.xlabel("Time")
        plt.ylabel("Retry Count")
        plt.tight_layout()
        path = os.path.join(outdir, "pubsub_retries_over_time.png")
        plt.savefig(path)
        plt.close()
        print(f"[PUBSUB] Saved plot: {path}")

    return {"total_delivered": delivered, "total_retries": retries}
