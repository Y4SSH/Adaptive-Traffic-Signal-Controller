from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.env.traffic_env import AdvancedTrafficEnv


def run_short(seed: int = 42, steps: int = 200):
    route = ROOT / 'configs' / f'demand.eval.{seed}.rou.xml'
    subprocess.run([sys.executable, str(ROOT / 'configs' / 'demand_generator.py'), str(seed), '--output', str(route)], check=True)
    env = AdvancedTrafficEnv(net_path=ROOT / 'configs' / 'intersection.net.xml', route_path=route, use_gui=False, verbose=False)
    obs, info = env.reset(seed=seed)
    print('reset info', info)
    try:
        for s in range(0, steps, 5):
            action = 0
            obs, reward, done, truncated, info = env.step(action)
            print(f"step={s} halting={info.get('halting_vector')} current_phase={info.get('current_phase')} cum_delay={info.get('cumulative_delay'):.1f}")
            if done or truncated:
                break
    finally:
        env.close()


if __name__ == '__main__':
    run_short(42, 200)
