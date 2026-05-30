from pathlib import Path
import xml.etree.ElementTree as ET

NET = Path('configs') / 'intersection.net.xml'


def main():
    tree = ET.parse(NET)
    root = tree.getroot()
    for tl in root.findall('tlLogic'):
        tid = tl.get('id')
        print(f'Traffic light: {tid}')
        phases = []
        for ph in tl.findall('phase'):
            state = ph.get('state') or ''
            phases.append(state)
        # try to find incLanes from junction
        junction = None
        for j in root.findall('junction'):
            if j.get('id') == tid or (j.get('type') == 'traffic_light' and junction is None):
                if j.get('id') == tid:
                    junction = j
                    break
                junction = j
        inc = junction.get('incLanes') if junction is not None else None
        lanes = inc.split() if inc else []
        print('Lanes (incLanes):', lanes)
        for i, state in enumerate(phases):
            greens = [lanes[idx] if idx < len(lanes) and ch in ('G','g') else None for idx, ch in enumerate(state)]
            greens = [g for g in greens if g]
            print(f'  Phase {i}: state={state} -> greens={greens}')


if __name__ == '__main__':
    main()
