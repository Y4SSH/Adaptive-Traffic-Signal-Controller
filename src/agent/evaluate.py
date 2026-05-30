from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"
NET_PATH = CONFIG_DIR / "intersection.net.xml"
MODEL_PATH = PROJECT_ROOT / "best_model.zip"
EVAL_SEEDS = [42, 101, 777, 1999, 2026]
BASELINE_PHASE_DURATION = 30
EVALUATION_LOG_PATH = PROJECT_ROOT / "eval_logs" / "evaluations.npz"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.env.traffic_env import AdvancedTrafficEnv, PHASE_STATES  # noqa: E402


@dataclass(frozen=True)
class EpisodeMetrics:
    mean_delay: float
    max_queue: float
    throughput: float


def generate_route_file(seed: int, mean_interval: float = 10.0, profile: str = "default", burst_intensity: float = 1.0, horizon: float = 3000.0) -> Path:
    route_path = CONFIG_DIR / f"demand.eval.{seed}.rou.xml"
    generator_script = CONFIG_DIR / "demand_generator.py"
    subprocess.run(
        [
            sys.executable,
            str(generator_script),
            str(seed),
            "--output",
            str(route_path),
            "--mean-interval",
            str(mean_interval),
            "--profile",
            profile,
            "--burst-intensity",
            str(burst_intensity),
            "--horizon",
            str(horizon),
        ],
        check=True,
    )
    return route_path


def create_env(route_path: Path, max_steps: int) -> Monitor:
    env = AdvancedTrafficEnv(net_path=NET_PATH, route_path=route_path, use_gui=False, max_steps=max_steps)
    return Monitor(env)


def run_fixed_time_baseline(route_path: Path, seed: int, max_steps: int) -> EpisodeMetrics:
    env = create_env(route_path, max_steps=max_steps)
    observation, info = env.reset(seed=seed)
    done = False
    truncated = False
    while not done and not truncated:
        phase_index = (int(info["current_step"]) // BASELINE_PHASE_DURATION) % len(PHASE_STATES)
        observation, reward, done, truncated, info = env.step(phase_index)
    env.close()
    return EpisodeMetrics(
        mean_delay=float(info["cumulative_delay"]),
        max_queue=float(info["max_queue"]),
        throughput=float(info["throughput"]),
    )


def run_dqn_policy(route_path: Path, seed: int, model: DQN, max_steps: int) -> EpisodeMetrics:
    env = create_env(route_path, max_steps=max_steps)
    observation, info = env.reset(seed=seed)
    done = False
    truncated = False
    while not done and not truncated:
        action, _ = model.predict(observation, deterministic=True)
        observation, reward, done, truncated, info = env.step(int(action))
    env.close()
    return EpisodeMetrics(
        mean_delay=float(info["cumulative_delay"]),
        max_queue=float(info["max_queue"]),
        throughput=float(info["throughput"]),
    )


def summarize_results(baseline_rows: list[dict], dqn_rows: list[dict]) -> pd.DataFrame:
    baseline_df = pd.DataFrame(baseline_rows)
    dqn_df = pd.DataFrame(dqn_rows)

    summary = pd.DataFrame(
        {
            "Metric": ["Mean Delay", "Max Queue", "Throughput"],
            "Baseline Mean": [
                baseline_df["mean_delay"].mean(),
                baseline_df["max_queue"].mean(),
                baseline_df["throughput"].mean(),
            ],
            "DQN Mean": [
                dqn_df["mean_delay"].mean(),
                dqn_df["max_queue"].mean(),
                dqn_df["throughput"].mean(),
            ],
        }
    )
    summary["Absolute Delta"] = summary["DQN Mean"] - summary["Baseline Mean"]
    summary["Relative Delta %"] = np.where(
        summary["Baseline Mean"].to_numpy() != 0,
        summary["Absolute Delta"] / summary["Baseline Mean"] * 100.0,
        0.0,
    )
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the DQN policy against a fixed-time baseline.")
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=EVAL_SEEDS,
        help="One or more integer seeds to evaluate.",
    )
    parser.add_argument("--mean-interval", type=float, default=10.0, help="Mean inter-arrival time in seconds.")
    parser.add_argument("--profile", choices=("default", "peak"), default="default", help="Demand profile to evaluate.")
    parser.add_argument("--burst-intensity", type=float, default=1.0, help="Peak profile burst scaling.")
    parser.add_argument("--horizon", type=float, default=3000.0, help="Demand horizon in seconds.")
    parser.add_argument("--max-steps", type=int, default=3600, help="Maximum steps per evaluation episode.")
    parser.add_argument("--output", type=Path, default=EVALUATION_LOG_PATH, help="Path to save evaluation results as .npz.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not NET_PATH.exists():
        raise FileNotFoundError(f"Missing SUMO network file: {NET_PATH}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing trained model file: {MODEL_PATH}. Run src/agent/train.py first."
        )

    model = DQN.load(str(MODEL_PATH))
    baseline_results: list[dict] = []
    dqn_results: list[dict] = []

    for seed in args.seeds:
        route_path = generate_route_file(
            seed,
            mean_interval=args.mean_interval,
            profile=args.profile,
            burst_intensity=args.burst_intensity,
            horizon=args.horizon,
        )
        baseline_metrics = run_fixed_time_baseline(route_path, seed, max_steps=args.max_steps)
        dqn_metrics = run_dqn_policy(route_path, seed, model, max_steps=args.max_steps)
        baseline_results.append({"seed": seed, **baseline_metrics.__dict__})
        dqn_results.append({"seed": seed, **dqn_metrics.__dict__})

    summary = summarize_results(baseline_results, dqn_results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        args.output,
        baseline=np.array(baseline_results, dtype=object),
        dqn=np.array(dqn_results, dtype=object),
        summary=summary.to_records(index=False),
    )
    print("\nEvaluation Summary Across Five Randomized Seeds")
    print(summary.to_string(index=False, float_format=lambda value: f"{value:,.3f}"))
    print(f"Saved evaluation results to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
