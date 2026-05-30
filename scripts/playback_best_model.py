import argparse
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stable_baselines3 import DQN
from src.env.traffic_env import AdvancedTrafficEnv


def generate_route(seed: int = 42, mean_interval: float = 5.0, profile: str = 'default', burst_intensity: float = 1.0, horizon: float = 3000.0):
    route = ROOT / 'configs' / f'demand.showcase.{seed}.rou.xml'
    subprocess.run(
        [
            sys.executable,
            str(ROOT / 'configs' / 'demand_generator.py'),
            str(seed),
            '--output',
            str(route),
            '--profile',
            profile,
            '--mean-interval',
            str(mean_interval),
            '--burst-intensity',
            str(burst_intensity),
            '--horizon',
            str(horizon),
        ],
        check=True,
    )
    return route


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Play back the trained agent in SUMO GUI.')
    parser.add_argument('--seed', type=int, default=42, help='Route generation seed.')
    parser.add_argument(
        '--mean-interval',
        type=float,
        default=5.0,
        help='Mean inter-arrival time in seconds; lower values create denser traffic.',
    )
    parser.add_argument(
        '--profile',
        choices=('default', 'peak'),
        default='default',
        help='Traffic profile to generate for playback.',
    )
    parser.add_argument(
        '--burst-intensity',
        type=float,
        default=1.0,
        help='Burst scale factor when using the peak profile.',
    )
    parser.add_argument(
        '--horizon',
        type=float,
        default=3000.0,
        help='Simulation horizon in seconds for generated demand.',
    )
    return parser.parse_args(argv)


def main(seed: int = 42, mean_interval: float = 5.0, profile: str = 'default', burst_intensity: float = 1.0, horizon: float = 3000.0):
    model_path = ROOT / 'best_model.zip'
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    route = generate_route(seed, mean_interval=mean_interval, profile=profile, burst_intensity=burst_intensity, horizon=horizon)
    model = DQN.load(str(model_path))
    env = AdvancedTrafficEnv(net_path=ROOT / 'configs' / 'intersection.net.xml', route_path=route, use_gui=True, verbose=True)

    obs, info = env.reset(seed=seed)
    done = False
    truncated = False
    try:
        while not done and not truncated:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(int(action))
            time.sleep(0.01)
    finally:
        env.close()


if __name__ == '__main__':
    args = parse_args()
    main(args.seed, args.mean_interval, args.profile, args.burst_intensity, args.horizon)
