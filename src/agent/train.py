from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"
SRC_DIR = PROJECT_ROOT / "src"
TRAIN_DEMAND_PATH = CONFIG_DIR / "demand.train.rou.xml"
NET_PATH = Path(os.environ.get("SUMO_NET_PATH", str(CONFIG_DIR / "intersection.net.xml")))
BEST_MODEL_PATH = PROJECT_ROOT / "best_model.zip"
LEARNING_CURVE_PATH = PROJECT_ROOT / "learning_curve.png"
EVAL_LOG_DIR = PROJECT_ROOT / "eval_logs"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure SUMO_HOME is available to spawned worker processes (prevents TraCI errors)
if "SUMO_HOME" not in os.environ:
    os.environ["SUMO_HOME"] = r"C:\Program Files (x86)\Eclipse\Sumo"
sumo_tools = os.path.join(os.environ["SUMO_HOME"], "tools")
if os.path.isdir(sumo_tools) and sumo_tools not in sys.path:
    sys.path.append(sumo_tools)

from src.env.traffic_env import AdvancedTrafficEnv  # noqa: E402


TRAIN_DEMAND_SEED = int(os.environ.get("TRAIN_DEMAND_SEED", "2026"))
TRAIN_TOTAL_TIMESTEPS = int(os.environ.get("TRAIN_TOTAL_TIMESTEPS", "5000"))
EVAL_FREQUENCY = 5_000


def ensure_route_file(route_path: Path, seed: int) -> Path:
    generator_script = CONFIG_DIR / "demand_generator.py"
    # Allow skipping generation for example routes (when using SUMO example networks)
    if os.environ.get("SKIP_ROUTE_GENERATION", "0") == "1":
        if route_path.exists():
            return route_path
        # if skipping but route doesn't exist, fall back to generation
    if not generator_script.exists():
        raise FileNotFoundError(f"Missing demand generator script: {generator_script}")
    subprocess.run(
        [sys.executable, str(generator_script), str(seed), "--output", str(route_path)],
        check=True,
    )
    return route_path


def make_env(route_path: Path, use_gui: bool):
    def _factory():
        env = AdvancedTrafficEnv(net_path=NET_PATH, route_path=route_path, use_gui=use_gui, verbose=False)
        return Monitor(env)

    return _factory


def build_model(train_env: DummyVecEnv) -> DQN:
    return DQN(
        policy="MlpPolicy",
        env=train_env,
        learning_rate=7.5e-4,
        buffer_size=50_000,
        batch_size=64,
        gamma=0.985,
        exploration_fraction=0.15,
        exploration_final_eps=0.02,
        verbose=1,
        seed=TRAIN_DEMAND_SEED,
        device="auto",
    )


def plot_learning_curve(eval_callback: EvalCallback) -> None:
    if not eval_callback.evaluations_results:
        return

    eval_means = np.array([float(np.mean(result)) for result in eval_callback.evaluations_results], dtype=np.float64)
    cumulative_rewards = np.cumsum(eval_means)
    episodes = np.arange(1, len(cumulative_rewards) + 1, dtype=np.int32)

    plt.figure(figsize=(10, 6), dpi=160)
    plt.plot(episodes, cumulative_rewards, marker="o", linewidth=2.0, color="#0b6efd")
    plt.xscale("log")
    plt.title("Cumulative Reward vs Episodes")
    plt.xlabel("Evaluation Episode Index (log scale)")
    plt.ylabel("Cumulative Reward")
    plt.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.7)
    plt.tight_layout()
    plt.savefig(LEARNING_CURVE_PATH, bbox_inches="tight")
    plt.close()


def main() -> int:
    if not NET_PATH.exists():
        raise FileNotFoundError(f"Missing SUMO network file: {NET_PATH}")

    route_path = ensure_route_file(TRAIN_DEMAND_PATH, TRAIN_DEMAND_SEED)
    eval_route_path = ensure_route_file(CONFIG_DIR / "demand.eval.validation.rou.xml", TRAIN_DEMAND_SEED + 1)

    train_env = DummyVecEnv([make_env(route_path, use_gui=False)])
    eval_env = DummyVecEnv([make_env(eval_route_path, use_gui=False)])

    BEST_MODEL_PATH.unlink(missing_ok=True)
    LEARNING_CURVE_PATH.unlink(missing_ok=True)
    EVAL_LOG_DIR.mkdir(parents=True, exist_ok=True)

    model = build_model(train_env)
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(PROJECT_ROOT),
        log_path=str(EVAL_LOG_DIR),
        eval_freq=EVAL_FREQUENCY,
        n_eval_episodes=3,
        deterministic=True,
        render=False,
        verbose=1,
    )

    model.learn(total_timesteps=TRAIN_TOTAL_TIMESTEPS, callback=eval_callback)
    model.save(str(PROJECT_ROOT / "final_model.zip"))
    plot_learning_curve(eval_callback)

    print(f"Best model saved to: {BEST_MODEL_PATH}")
    print(f"Learning curve saved to: {LEARNING_CURVE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
