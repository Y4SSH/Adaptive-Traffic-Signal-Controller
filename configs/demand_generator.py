from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

VEHICLE_TYPE_ID = "passenger"
VEHICLE_TYPE_PROPS = {
    "accel": "2.6",
    "decel": "4.5",
    "length": "5.0",
    "maxSpeed": "13.89",
}

ROUTES = {
    "north_to_south": "north_in south_out",
    "south_to_north": "south_in north_out",
    "east_to_west": "east_in west_out",
    "west_to_east": "west_in east_out",
}


@dataclass(frozen=True)
class VehiclePlan:
    depart: float
    route_id: str
    prefix: str


def _sample_arrivals(start: float, end: float, mean_interval: float, rng: random.Random) -> list[float]:
    arrivals: list[float] = []
    current_time = float(start)
    rate = 1.0 / float(mean_interval)
    while True:
        current_time += rng.expovariate(rate)
        if current_time >= end:
            break
        arrivals.append(round(current_time, 3))
    return arrivals


def build_vehicle_plan(seed: int, mean_interval: float = 10.0, profile: str = "default", horizon_end: float = 3000.0, burst_intensity: float = 1.0) -> list[VehiclePlan]:
    rng = random.Random(seed)
    plans: list[VehiclePlan] = []

    # Keep the default demand balanced across all directions so no axis is
    # consistently favored by the policy or by the simulator.
    route_ids = list(ROUTES.keys())
    horizon_start = 0.0

    # Support a realistic, time-varying `peak` profile with stochastic surges.
    if profile == "peak":
        # piecewise schedule over the simulation horizon (seconds)
        # morning ramp -> peak -> shoulder -> evening surge
        windows = [
            (0.0, horizon_end * 0.15, mean_interval * 1.5),
            (horizon_end * 0.15, horizon_end * 0.35, max(0.5, mean_interval * 0.25)),
            (horizon_end * 0.35, horizon_end * 0.65, mean_interval),
            (horizon_end * 0.65, horizon_end * 0.85, max(0.5, mean_interval * 0.4)),
            (horizon_end * 0.85, horizon_end, mean_interval * 1.8),
        ]
        arrivals = []
        for (s, e, mi) in windows:
            arrivals.extend(_sample_arrivals(s, e, mi, rng))

        # Add burst events to model unpredictability: random bursts of vehicles
        burst_count = max(1, int(5 * burst_intensity))
        for _ in range(burst_count):
            burst_time = rng.uniform(horizon_start, horizon_end)
            # burst size proportional to intensity
            burst_size = rng.randint(8, int(30 * burst_intensity))
            for i in range(burst_size):
                # jitter within a short window (0-10s)
                arrivals.append(round(burst_time + rng.random() * 10.0, 3))
    else:
        arrivals = _sample_arrivals(horizon_start, horizon_end, mean_interval, rng)

    for index, depart_time in enumerate(arrivals):
        route_id = rng.choice(route_ids)
        plans.append(
            VehiclePlan(
                depart=depart_time,
                route_id=route_id,
                prefix=f"{route_id}_{index:05d}",
            )
        )

    plans.sort(key=lambda item: (item.depart, item.route_id, item.prefix))
    return plans


def generate_demand(seed: int, output_path: Path, mean_interval: float = 10.0, profile: str = "default", horizon_end: float = 3000.0, burst_intensity: float = 1.0) -> Path:
    plans = build_vehicle_plan(seed, mean_interval=mean_interval, profile=profile, horizon_end=horizon_end, burst_intensity=burst_intensity)

    root = ET.Element("routes")
    ET.SubElement(
        root,
        "vType",
        attrib={"id": VEHICLE_TYPE_ID, **VEHICLE_TYPE_PROPS},
    )

    for route_id, edge_sequence in ROUTES.items():
        ET.SubElement(root, "route", attrib={"id": route_id, "edges": edge_sequence})

    for sequence_number, plan in enumerate(plans):
        vehicle_id = f"veh_{seed}_{sequence_number:06d}"
        ET.SubElement(
            root,
            "vehicle",
            attrib={
                "id": vehicle_id,
                "type": VEHICLE_TYPE_ID,
                "route": plan.route_id,
                "depart": f"{plan.depart:.3f}",
                "departLane": "random",
                "departSpeed": "max",
            },
        )

    tree = ET.ElementTree(root)
    try:
        ET.indent(tree, space="    ")
    except AttributeError:
        pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    return output_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic SUMO traffic demand.")
    parser.add_argument("seed", type=int, help="Random seed used to build the stochastic arrival schedule.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().with_name("demand.rou.xml"),
        help="Destination route file path.",
    )
    parser.add_argument(
        "--mean-interval",
        type=float,
        default=10.0,
        help="Mean inter-arrival time between vehicles in seconds (lower = higher traffic frequency).",
    )
    parser.add_argument(
        "--profile",
        choices=("default", "peak"),
        default="default",
        help="Traffic profile to generate. 'peak' creates time-varying arrivals with bursts.",
    )
    parser.add_argument(
        "--horizon",
        type=float,
        default=3000.0,
        help="Total simulation horizon in seconds.",
    )
    parser.add_argument(
        "--burst-intensity",
        type=float,
        default=1.0,
        help="Scale factor for random burst sizes (higher = larger unpredictable surges).",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    generated_path = generate_demand(
        args.seed,
        args.output,
        mean_interval=args.mean_interval,
        profile=args.profile,
        horizon_end=args.horizon,
        burst_intensity=args.burst_intensity,
    )
    print(f"Generated demand file: {generated_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
