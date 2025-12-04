# analyze.py
import argparse
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html
import dash.dependencies as deps

# -------------------------------
# Load Metrics
# -------------------------------
def load_metrics(path):
    metrics_file = os.path.join(path, "metrics.csv")
    if not os.path.exists(metrics_file):
        raise FileNotFoundError(f"metrics.csv not found in: {path}")

    df = pd.read_csv(metrics_file)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    return df

# -------------------------------
# Load events.log
# -------------------------------
def load_logs(path):
    log_file = os.path.join(path, "events.log")
    if not os.path.exists(log_file):
        return []

    with open(log_file, "r") as f:
        return f.readlines()

# -------------------------------
# Summary Stats
# -------------------------------
def summary_stats(df, outdir):
    stats = {}
    def p95(x): return x.quantile(0.95) if len(x) else 0

    for metric in ["auth_latency", "turn_latency", "pubsub_delay"]:
        d = df[df["metric"] == metric]["value"]
        stats[f"{metric}_mean"] = d.mean() if len(d) else 0
        stats[f"{metric}_95p"] = p95(d)

    q = df[df["metric"] == "queue_length"]["value"]
    stats["queue_max"] = q.max() if len(q) else 0
    stats["queue_mean"] = q.mean() if len(q) else 0

    stats_df = pd.DataFrame([stats])
    csv_path = os.path.join(outdir, "summary_stats.csv")
    stats_df.to_csv(csv_path, index=False)
    print(f"[OK] Saved summary stats: {csv_path}")
    return stats_df

# -------------------------------
# Matplotlib plots
# -------------------------------
def plot_smoothed(df, metric, outdir, window=50):
    d = df[df['metric'] == metric]
    if d.empty: return

    d = d.sort_values('timestamp')
    d['rolling'] = d['value'].rolling(window=window, min_periods=1).mean()

    plt.figure(figsize=(10,5))
    plt.plot(d['timestamp'], d['rolling'], label=f"{metric} (rolling)")
    plt.scatter(d['timestamp'], d['value'], s=4, alpha=0.2)
    plt.title(f"{metric} (Smoothed)")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, f"{metric}.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Saved: {path}")

def plot_distribution(df, metric, outdir):
    d = df[df['metric'] == metric]
    if d.empty: return

    plt.figure(figsize=(8,5))
    plt.hist(d['value'], bins=40, alpha=0.7)
    plt.title(f"{metric} Distribution")
    plt.xlabel("Value")
    plt.ylabel("Count")
    plt.tight_layout()
    path = os.path.join(outdir, f"{metric}_distribution.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Saved distribution: {path}")

# -------------------------------
# Plotly Dashboard
# -------------------------------
def launch_dashboard(df):
    app = Dash(__name__)
    metrics = df['metric'].unique()

    app.layout = html.Div([
        html.H1("Simulation Analytics Dashboard", style={"textAlign": "center"}),

        dcc.Dropdown(
            id="metric-dropdown",
            options=[{"label": m, "value": m} for m in metrics],
            value="auth_latency",
            clearable=False
        ),

        dcc.Graph(id="time-series-plot"),
        dcc.Graph(id="distribution-plot")
    ])

    @app.callback(
        deps.Output("time-series-plot", "figure"),
        deps.Input("metric-dropdown", "value")
    )
    def update_timeseries(metric):
        d = df[df['metric'] == metric].sort_values('timestamp')
        if d.empty: return go.Figure()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d['timestamp'], y=d['value'], mode='markers', name='raw', opacity=0.3))
        fig.add_trace(go.Scatter(x=d['timestamp'], y=d['value'].rolling(50).mean(), mode='lines', name='smoothed'))
        fig.update_layout(title=f"{metric} Over Time", xaxis_title="Time", yaxis_title="Value")
        return fig

    @app.callback(
        deps.Output("distribution-plot", "figure"),
        deps.Input("metric-dropdown", "value")
    )
    def update_distribution(metric):
        d = df[df['metric'] == metric]
        if d.empty: return go.Figure()

        fig = px.histogram(d, x="value", nbins=50, title=f"{metric} Distribution")
        return fig

    print("\n[INFO] Dashboard running at http://127.0.0.1:8050")
    app.run(debug=False)

# -------------------------------
# Main
# -------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=False, help="Path to run folder (e.g., outputs/run_xxx)")
    parser.add_argument("--dashboard", action="store_true", help="Launch interactive dashboard")
    args = parser.parse_args()

    # Resolve project root relative to this script
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Auto-detect latest run if not provided
    run_path = args.run
    if not run_path:
        runs = sorted(glob.glob(os.path.join(PROJECT_ROOT, "outputs/run_*")), reverse=True)
        if not runs:
            raise Exception("No run folders found in outputs/")
        run_path = runs[0]

    if not os.path.isdir(run_path):
        raise Exception(f"Run folder not found: {run_path}")

    print(f"[INFO] Loading metrics from {run_path}...")
    df = load_metrics(run_path)
    logs = load_logs(run_path)
    print(f"[INFO] Loaded {len(df)} metric records and {len(logs)} log lines")

    summary_stats(df, run_path)

    # Matplotlib plots
    for metric in ["auth_latency", "turn_latency", "pubsub_delay", "queue_length"]:
        plot_smoothed(df, metric, run_path)
        plot_distribution(df, metric, run_path)

    # Launch interactive Plotly dashboard if requested
    if args.dashboard:
        launch_dashboard(df)

if __name__ == "__main__":
    main()
