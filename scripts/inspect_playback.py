from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stable_baselines3 import DQN
from src.env.traffic_env import AdvancedTrafficEnv


def generate_route(seed: int = 42):
    route = ROOT / 'configs' / f'demand.eval.{seed}.rou.xml'
    subprocess.run([sys.executable, str(ROOT / 'configs' / 'demand_generator.py'), str(seed), '--output', str(route)], check=True)
    return route


def main(seed: int = 42):
    model_path = ROOT / 'best_model.zip'
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    route = generate_route(seed)
    model = DQN.load(str(model_path))
    env = AdvancedTrafficEnv(net_path=ROOT / 'configs' / 'intersection.net.xml', route_path=route, use_gui=True, verbose=False)

    obs, info = env.reset(seed=seed)
    print('Reset info:', info)
    done = False
    truncated = False
    step = 0
    try:
        while not done and not truncated and step < 200:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(int(action))
            try:
                cur_state = __import__('traci').trafficlight.getRedYellowGreenState(env.traffic_light_id)
            except Exception:
                cur_state = None
            print(f"step={step} action={int(action)} phase={info.get('current_phase')} cum_delay={info.get('cumulative_delay'):.1f} max_queue={info.get('max_queue')} throughput={info.get('throughput')} cur_state={cur_state}")
            print('halting:', info.get('halting_vector'))
            step += 1
            time.sleep(0.05)
    finally:
        env.close()


if __name__ == '__main__':
    main(42)
