from pathlib import Path
import time
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.env.traffic_env import AdvancedTrafficEnv


def main(seed: int = 42, route: Path | None = None, steps: int = 200):
    if route is None:
        route = ROOT / 'configs' / f'demand.random.{seed}.rou.xml'
    print('Using route:', route)
    env = AdvancedTrafficEnv(net_path=ROOT / 'configs' / 'intersection.net.xml', route_path=route, use_gui=True, verbose=True)
    obs, info = env.reset(seed=seed)
    print('Reset info:', info)
    done = False
    truncated = False
    step = 0
    phase_count = env.action_space.n
    try:
        while not done and not truncated and step < steps:
            action = step % phase_count
            obs, reward, done, truncated, info = env.step(int(action))
            try:
                cur_state = __import__('traci').trafficlight.getRedYellowGreenState(env.traffic_light_id)
            except Exception:
                cur_state = None
            print(f"step={step} action={action} phase={info.get('current_phase')} cum_delay={info.get('cumulative_delay'):.1f} max_queue={info.get('max_queue')} throughput={info.get('throughput')} cur_state={cur_state}")
            print('halting:', info.get('halting_vector'))
            step += 1
            time.sleep(0.05)
    finally:
        env.close()


if __name__ == '__main__':
    main()
