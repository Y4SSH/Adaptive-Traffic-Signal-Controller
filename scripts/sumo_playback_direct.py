import os
import sys
import time
from pathlib import Path

# Ensure SUMO tools on path
if 'SUMO_HOME' not in os.environ:
    os.environ['SUMO_HOME'] = r"C:\Program Files (x86)\Eclipse\Sumo"
sumo_tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
if os.path.isdir(sumo_tools) and sumo_tools not in sys.path:
    sys.path.append(sumo_tools)

try:
    import traci
except Exception as e:
    print('traci import failed:', e)
    raise


def run(route_path: Path, net_path: Path, steps: int = 200, use_gui: bool = True):
    binary = 'sumo-gui' if use_gui else 'sumo'
    sumo_bin = None
    # try to find in PATH
    from shutil import which

    sumo_bin = which(binary)
    if not sumo_bin:
        sumo_home = os.environ.get('SUMO_HOME')
        if sumo_home:
            candidate = Path(sumo_home) / 'bin' / (binary + '.exe')
            if candidate.exists():
                sumo_bin = str(candidate)
    if not sumo_bin:
        raise FileNotFoundError('SUMO binary not found; set SUMO_HOME or add to PATH')

    cmd = [
        sumo_bin,
        '--no-step-log', 'true',
        '--time-to-teleport', '-1',
        '--step-length', '1',
        '-n', str(net_path),
        '-r', str(route_path),
        '--quit-on-end', 'true',
    ]
    print('Starting SUMO:', ' '.join(cmd))
    traci.start(cmd)
    log_path = Path(net_path).with_name('playback_diagnostics.log')
    try:
        fh = open(log_path, 'w', encoding='utf-8')
    except Exception:
        fh = None
    try:
        for step in range(steps):
            if traci.simulation.getMinExpectedNumber() <= 0:
                print('No expected vehicles remaining; exiting')
                if fh:
                    fh.write(f'No expected vehicles remaining; exiting at step={step}\n')
                break
            traci.simulationStep()
            # print traffic light states and lane halting counts
            try:
                tls = traci.trafficlight.getIDList()
                for tid in tls:
                    state = traci.trafficlight.getRedYellowGreenState(tid)
                    print(f'step={step} TL={tid} state={state}')
            except Exception:
                pass
            lanes_to_check = [
                'north_in_0','north_in_1','north_in_2',
                'south_in_0','south_in_1','south_in_2',
                'east_in_0','east_in_1','east_in_2',
                'west_in_0','west_in_1','west_in_2',
            ]
            halts = {}
            for lid in lanes_to_check:
                try:
                    halts[lid] = traci.lane.getLastStepHaltingNumber(lid)
                except Exception:
                    halts[lid] = None
            line = f'halts: {halts}'
            print(line)
            if fh:
                fh.write(f'step={step} {line}\n')
            time.sleep(0.05)
    finally:
        if fh:
            fh.close()
        try:
            traci.close()
        except Exception:
            pass


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    route = root / 'configs' / 'demand.random.42.rou.xml'
    net = root / 'configs' / 'intersection.net.xml'
    use_gui = True
    if '--nogui' in sys.argv:
        use_gui = False
    run(route, net, steps=200, use_gui=use_gui)
