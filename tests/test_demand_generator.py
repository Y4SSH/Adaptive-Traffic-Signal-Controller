from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path.cwd()


def generate_route(tmp_path: Path, seed: int, profile: str = "default", mean_interval: float = 10.0, burst_intensity: float = 1.0) -> Path:
    output = tmp_path / f"demand.{profile}.{seed}.rou.xml"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "configs" / "demand_generator.py"),
            str(seed),
            "--output",
            str(output),
            "--profile",
            profile,
            "--mean-interval",
            str(mean_interval),
            "--burst-intensity",
            str(burst_intensity),
        ],
        check=True,
    )
    return output


def count_vehicles(route_path: Path) -> int:
    root = ET.parse(route_path).getroot()
    return sum(1 for element in root.findall("vehicle"))


def test_peak_profile_generates_more_vehicles(tmp_path):
    default_route = generate_route(tmp_path, seed=42, profile="default", mean_interval=5.0)
    peak_route = generate_route(tmp_path, seed=42, profile="peak", mean_interval=5.0, burst_intensity=1.5)

    assert count_vehicles(peak_route) > count_vehicles(default_route)


def test_vehicle_depart_lane_is_random(tmp_path):
    route = generate_route(tmp_path, seed=101, profile="peak", mean_interval=5.0, burst_intensity=1.0)
    root = ET.parse(route).getroot()

    depart_lanes = {vehicle.get("departLane") for vehicle in root.findall("vehicle")}

    assert depart_lanes == {"random"}
