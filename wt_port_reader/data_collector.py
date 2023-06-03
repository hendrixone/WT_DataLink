from enum import Enum

import numpy as np
import requests

state_url = 'http://localhost:8111/state'
map_object_url = 'http://localhost:8111/map_obj.json'
indicators_url = 'http://localhost:8111/indicators'
map_img_url = 'http://localhost:8111/map.img?gen=3'
map_info_url = 'http://localhost:8111/map_info.json'

TIMEOUT = 0.5


class GameStatus(Enum):
    NOT_RUNNING = 0
    MENU = 1
    NOT_SPAWNED = 2
    RUNNING = 3
    LOADING = 4


def get_raw_data(url):
    response = requests.get(url, timeout=TIMEOUT)
    if response.ok:
        return response
    else:
        raise Exception("Bad Conn")


def get_map_img():
    return get_raw_data(map_img_url).content


def get_state():
    return get_raw_data(state_url).json()


def get_indicators():
    return get_raw_data(state_url).json()

def get_map_info():
    return get_raw_data(map_info_url).json()


def get_map_objs():
    return get_raw_data(map_object_url).json()


def get_game_status():
    try:
        map_info = get_map_info()
        if map_info['valid']:
            map_objs = get_map_objs()
            for obj in map_objs:
                if obj['icon'] == "Player":
                    return GameStatus.RUNNING
            return GameStatus.NOT_SPAWNED

        else:
            return GameStatus.MENU
    except requests.exceptions.ConnectionError:
        return GameStatus.NOT_RUNNING
    except requests.exceptions.ReadTimeout:
        return GameStatus.LOADING


def get_telemetry():
    state = get_state()
    return {key: float(value) for key, value in state.items() if key in
            ['H, m', 'TAS, km/h', 'AoA, deg', 'AoS, deg', 'Vy, m/s']}


def get_aircraft_type():
    indicators = get_indicators()
    return indicators['type']


def get_attitude():
    indicators = get_indicators()
    if indicators['valid'] == 'false':
        return 0
    indicators = {key: -float(value) for key, value in indicators.items() if key in
                  ['aviahorizon_roll', 'aviahorizon_pitch', 'compass']}
    indicators['compass'] = -indicators['compass']
    return indicators


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


def get_aircraft_name():
    state = get_state()
    return state['type']


# def start_listen(path, map_size, game_speed, update_interval):
#     # update interval millisecond
#     update_interval = 0.01
#     coord, telemetry, attitude, earth_relative_airspeed = get_data(map_size)


def get_simple_data():
    map_obj = get_map_objs()
    telemetry = get_telemetry()
    # get position and direction
    data = 0
    for obj in map_obj:
        if obj['icon'] == 'Player':
            data = {key: float(value) for key, value in obj.items() if key in
                    ['x', 'y', 'dx', 'dy']}
    data["altitude"] = telemetry['H, m']
    return data


if __name__ == '__main__':
    print(get_game_status())
