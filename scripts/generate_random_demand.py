from pathlib import Path
import random
import xml.etree.ElementTree as ET
import argparse


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


def generate_random(seed: int, output: Path, min_mean: float = 2.0, max_mean: float = 20.0, horizon: float = 3000.0):
    rng = random.Random(seed)
    routes = ["north_to_south", "south_to_north", "east_to_west", "west_to_east"]

    # sample different means for each route; add tiny jitter to guarantee differences
    means = []
    for i in range(len(routes)):
        m = rng.uniform(min_mean, max_mean)
        m += i * 1e-3
        means.append(m)

    plans = []
    seq = 0
    for route_id, mean in zip(routes, means):
        arrivals = _sample_arrivals(0.0, horizon, mean, rng)
        for dep in arrivals:
            plans.append((dep, route_id, seq))
            seq += 1

    plans.sort()

    root = ET.Element('routes')
    ET.SubElement(root, 'vType', attrib={'id': 'passenger', 'accel': '2.6', 'decel': '4.5', 'length': '5.0', 'maxSpeed': '13.89'})
    ET.SubElement(root, 'route', attrib={'id': 'north_to_south', 'edges': 'north_in south_out'})
    ET.SubElement(root, 'route', attrib={'id': 'south_to_north', 'edges': 'south_in north_out'})
    ET.SubElement(root, 'route', attrib={'id': 'east_to_west', 'edges': 'east_in west_out'})
    ET.SubElement(root, 'route', attrib={'id': 'west_to_east', 'edges': 'west_in east_out'})

    for idx, (depart, route_id, seq) in enumerate(sorted(plans)):
        ET.SubElement(root, 'vehicle', attrib={
            'id': f'veh_{seed}_{idx:06d}',
            'type': 'passenger',
            'route': route_id,
            'depart': f'{depart:.3f}',
            'departLane': 'random',
            'departSpeed': 'max',
        })

    tree = ET.ElementTree(root)
    try:
        ET.indent(tree, space='    ')
    except Exception:
        pass
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding='utf-8', xml_declaration=True)
    print(f"Generated randomized demand: {output} (means={{}})".format({r: f"{m:.3f}" for r, m in zip(routes, means)}))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('seed', type=int)
    p.add_argument('--output', type=Path, default=Path('configs') / f'demand.random.{{seed}}.rou.xml')
    p.add_argument('--min', type=float, default=2.0)
    p.add_argument('--max', type=float, default=20.0)
    p.add_argument('--horizon', type=float, default=3000.0)
    return p.parse_args()


def main():
    args = parse_args()
    out = args.output
    if '{seed}' in str(out):
        out = Path(str(out).format(seed=args.seed))
    generate_random(args.seed, out, min_mean=args.min, max_mean=args.max, horizon=args.horizon)


if __name__ == '__main__':
    main()
