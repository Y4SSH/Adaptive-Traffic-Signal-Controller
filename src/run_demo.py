from time import sleep

from src.env.traffic_env import AdvancedTrafficEnv


def main() -> None:
    net = "configs/intersection.net.xml"
    route = "configs/demand.seed42.rou.xml"
    env = AdvancedTrafficEnv(net_path=net, route_path=route, use_gui=True, max_steps=600)
    try:
        obs, info = env.reset(seed=42)
        print("Reset: ", info)
        step = 0
        current_phase = int(info.get("current_phase", 0))
        while True:
            # change phase every 30 steps to demonstrate switching
            if step % 30 == 0 and step > 0:
                action = (current_phase + 1) % env.action_space.n
            else:
                action = current_phase

            obs, reward, terminated, truncated, info = env.step(int(action))
            current_phase = int(info.get("current_phase", current_phase))
            step += 1
            print(f"step={step} phase={current_phase} reward={reward:.2f} max_queue={info.get('max_queue')}")
            sleep(0.05)
            if terminated or truncated:
                print("Simulation finished")
                break
    finally:
        env.close()


if __name__ == "__main__":
    main()
