import json


def write_config_to_file(config, config_file):
    """Write json config to file."""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)


def read_config_from_file(config_file):
    """Read json config from file."""
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


class Config:
    def __init__(self):
        self.active_map = True
        self.active_hmd = False

        self.map_size = 20
        self.zoom = 1

        self.x = 50
        self.y = 300

        self.player_center = False
