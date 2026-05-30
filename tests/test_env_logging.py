from pathlib import Path
import os
import shutil
import subprocess
import sys

import pytest


def ensure_route(seed: int = 42) -> Path:
    route = Path("configs") / f"demand.eval.{seed}.rou.xml"
    if not route.exists():
        subprocess.run([sys.executable, "configs/demand_generator.py", str(seed), "--output", str(route)], check=True)
    return route


def test_env_logging_basic():
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))

    if not os.environ.get("SUMO_HOME") and shutil.which("sumo") is None and shutil.which("sumo-gui") is None:
        pytest.skip("SUMO is not available in this environment")

    route = ensure_route(42)

    from src.env.traffic_env import AdvancedTrafficEnv  # noqa: E402

    env = AdvancedTrafficEnv(net_path=Path("configs") / "intersection.net.xml", route_path=route, use_gui=False, verbose=False)
    obs, info = env.reset(seed=42)
    assert isinstance(info, dict)
    assert "current_step" in info

    obs, reward, done, truncated, info = env.step(0)
    assert "cumulative_delay" in info
    assert "throughput" in info
    env.close()
