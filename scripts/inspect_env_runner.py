import os
import sys
from pathlib import Path

# ensure repo root is on sys.path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from src.env.traffic_env import AdvancedTrafficEnv

# default net/route (use project net if present)
net = os.environ.get('NET_PATH') or str(repo_root / 'configs' / 'intersection.net.xml')
route = os.environ.get('ROUTE_PATH') or str(repo_root / 'configs' / 'demand.train.rou.xml')

print('Using net:', net)
print('Using route:', route)

env = AdvancedTrafficEnv(net_path=net, route_path=route, use_gui=False, verbose=True)
print('Detected traffic_light_id:', env.traffic_light_id)
print('Detected lane_order len:', len(env._lane_order))
print('Detected lane_order:', env._lane_order)
print('Detected phase_states len:', len(env._phase_states))
print('Phase states sample:', env._phase_states[:10])
