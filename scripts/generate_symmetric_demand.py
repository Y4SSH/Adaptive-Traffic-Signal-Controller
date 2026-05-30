from pathlib import Path
import random
import xml.etree.ElementTree as ET
import argparse


def generate_symmetric(seed: int, output: Path, mean_interval: float = 10.0):
    rng = random.Random(seed)
    plans = []
    routes = ["north_to_south", "south_to_north", "east_to_west", "west_to_east"]
    # symmetric: same mean interval for all routes across full horizon
    start, end = 0.0, 3000.0
    rate = 1.0 / float(mean_interval)
    current = start
    seq = 0
    while True:
        # sample interarrival
        current += rng.expovariate(rate)
        if current >= end:
            break
        route = rng.choice(routes)
        plans.append((current, route, seq))
        seq += 1

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
            'departLane': 'best',
            'departSpeed': 'max',
        })

    tree = ET.ElementTree(root)
    try:
        ET.indent(tree, space='    ')
    except Exception:
        pass
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding='utf-8', xml_declaration=True)
    print(f'Generated symmetric demand: {output} (mean_interval={mean_interval})')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('seed', type=int)
    p.add_argument('--output', type=Path, default=Path('configs') / f'demand.eval.{{seed}}.rou.xml')
    p.add_argument('--mean', type=float, default=10.0)
    return p.parse_args()


def main():
    args = parse_args()
    out = args.output
    if '{seed}' in str(out):
        out = Path(str(out).format(seed=args.seed))
    generate_symmetric(args.seed, out, mean_interval=args.mean)


if __name__ == '__main__':
    main()
