from src.env.traffic_env import AdvancedTrafficEnv

net='C:/Program Files (x86)/Eclipse/Sumo/tools/game/cross/cross.net.xml'
route='C:/Program Files (x86)/Eclipse/Sumo/tools/game/cross/cross.rou.xml'
env=AdvancedTrafficEnv(net_path=net, route_path=route, use_gui=False, verbose=True)
print('Detected traffic_light_id:', env.traffic_light_id)
print('Detected lane_order len:', len(env._lane_order))
print('Detected lane_order:', env._lane_order)
print('Detected phase_states len:', len(env._phase_states))
print('Phase states sample:', env._phase_states[:10])
