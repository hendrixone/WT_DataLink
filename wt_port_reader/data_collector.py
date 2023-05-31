import numpy as np
import requests


state_url = 'http://localhost:8111/state'
# state_url = 'http://192.168.31.126:8111/state'
map_object_url = 'http://localhost:8111/map_obj.json'
# map_object_url = 'http://192.168.31.126:8111/map_obj.json'
indicators_url = 'http://localhost:8111/indicators'
# indicators_url = 'http://192.168.31.126:8111/indicators'

TIMEOUT = 1

def get_telemetry():
    state_response = requests.get(state_url)
    if state_response.ok:
        state = state_response.json()
        return {key: float(value) for key, value in state.items() if key in
                ['H, m', 'TAS, km/h', 'AoA, deg', 'AoS, deg', 'Vy, m/s']}
    else:
        raise Exception("Bad Conn")


def get_map_objs():
    map_object_response = requests.get(map_object_url, timeout=TIMEOUT)
    if map_object_response.ok:
        map_objs = map_object_response.json()
        return map_objs
    else:
        raise Exception("Bad Conn")


def get_attitude():
    indicator_response = requests.get(indicators_url)
    if indicator_response.ok:
        indicators = indicator_response.json()
        if indicators['valid'] == 'false':
            return 0
        indicators = {key: -float(value) for key, value in indicators.items() if key in
                      ['aviahorizon_roll', 'aviahorizon_pitch', 'compass']}
        indicators['compass'] = -indicators['compass']
        return indicators
    else:
        raise Exception("Bad Conn")


# return the current data of the selected aircraft
def get_data(map_size):
    telemetry = get_telemetry()
    map_object = get_map_objs()
    attitude = get_attitude()
    coord = 0
    for obj in map_object:
        if obj['icon'] == 'Player':
            coord = {key: float(value) * map_size for key, value in obj.items() if key in
                     ['x', 'y', 'dx', 'dy']}
            coord['x'] = 1 - coord['x']
    earth_relative_airspeed = calculate_earth_relative_airspeed(telemetry, attitude, coord)
    return coord, telemetry, attitude, earth_relative_airspeed


"""
Calculate the earth relative TAS vector using:

Aos, AoA, heading, Roll, Pitch, TAS

---------------------------------------------

The calculation will be as followed:
1. Calculate the vector of TAS from fixed body reference using AoA, AoS
2. Rotate the vector using the rotation matrices Rx, Ry, Rz calculated using attitude of the aircraft

-----------------------------------------------------------------------------------------------------

WT doesn't save indicators data from other aircraft, thus the flight data have to be calculated in other way
"""


def calculate_earth_relative_airspeed(telemetry, attitude, coord):
    beta = -np.radians(telemetry['AoS, deg'])
    alpha = -np.radians(telemetry['AoA, deg'])
    heading = np.radians(attitude['compass'] - 90)
    roll = np.radians(-attitude['aviahorizon_roll'])
    pitch = np.radians(-attitude['aviahorizon_pitch'])
    TAS = telemetry['TAS, km/h'] * 1000 / 3600

    # Calculate body-relative airspeed vector
    U = TAS * np.cos(alpha) * np.cos(beta)
    V = TAS * np.sin(beta)
    W = TAS * np.sin(alpha) * np.cos(beta)
    body_relative_airspeed = np.array([U, V, W])

    # Define rotation matrices
    R_roll = np.array([[1, 0, 0],
                       [0, np.cos(roll), -np.sin(roll)],
                       [0, np.sin(roll), np.cos(roll)]])

    R_pitch = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                        [0, 1, 0],
                        [-np.sin(pitch), 0, np.cos(pitch)]])

    R_heading = np.array([[np.cos(heading), -np.sin(heading), 0],
                          [np.sin(heading), np.cos(heading), 0],
                          [0, 0, 1]])

    # Combine rotation matrices
    R = R_heading @ R_pitch @ R_roll

    # Calculate Earth-relative airspeed vector
    earth_relative_airspeed = R @ body_relative_airspeed

    return earth_relative_airspeed

def start_listen(path, map_size, game_speed, update_interval):
    # update interval millisecond
    update_interval = 0.01
    coord, telemetry, attitude, earth_relative_airspeed = get_data(map_size)

def get_simple_data():
    map_obj = get_map_objs()
    telemetry = get_telemetry()
    # get position and direction
    data = 0
    for obj in map_obj:
        if obj['icon'] == 'Player':
            data = {key: float(value) for key, value in obj.items() if key in
                     ['x', 'y', 'dx', 'dy']}
    data["alt"] = telemetry['H, m']
    return data


if __name__ == '__main__':
    print("Hi")
