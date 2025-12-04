# run_validation.py
import os
import glob
import pandas as pd

from validation_scripts.verify_queue_match import verify_queue_match
from validation_scripts.verify_turns_latency import verify_turns_latency
from validation_scripts.verify_pubsub import verify_pubsub
from validation_scripts.verify_arrivals import verify_arrivals

# -------------------------------
# Load metrics CSV
# -------------------------------
def load_metrics(run_path):
    metrics_file = os.path.join(run_path, "metrics.csv")
    if not os.path.exists(metrics_file):
        raise FileNotFoundError(f"metrics.csv not found in {run_path}")
    df = pd.read_csv(metrics_file)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    return df

# -------------------------------
# Main validation runner
# -------------------------------
def main():
    # Auto-detect latest run folder relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    runs = sorted(glob.glob(os.path.join(project_root, "outputs/run_*")), reverse=True)
    if not runs:
        raise Exception("No run folders found in outputs/")
    run_path = runs[0]
    print(f"[INFO] Validating run: {run_path}")

    # Load metrics
    metrics_df = load_metrics(run_path)

    # Ensure results folder exists
    results_dir = os.path.join(project_root, "validation/results")
    os.makedirs(results_dir, exist_ok=True)

    # Run validation scripts
    queue_stats = verify_queue_match(metrics_df, results_dir)
    turn_stats = verify_turns_latency(metrics_df, results_dir)
    pubsub_stats = verify_pubsub(metrics_df, results_dir)
    arrivals_stats = verify_arrivals(metrics_df, results_dir)

    # Aggregate summary
    summary = {**queue_stats, **turn_stats, **pubsub_stats, **arrivals_stats}
    summary_df = pd.DataFrame([summary])
    summary_csv = os.path.join(results_dir, "validation_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"[INFO] Validation summary saved: {summary_csv}")

if __name__ == "__main__":
    main()
