from copy import copy
import toml
from dataclasses import dataclass

from . import common


@dataclass
class Config:
    def __init__(self, config: dict) -> None:
        self.download_path: str = config["download_path"]
        self.ao3_username: str = config["ao3_username"]
        self.ao3_password: str = config["ao3_password"]
        self.devices: list[common.Device] = list(
            map(lambda device: common.Device(**device), config["devices"])
        )
        self.fandom_map: dict[str, str] = config["fandom_map"]
        self.fandom_filter: dict[str, list[str]] = config["fandom_filter"]

    def to_json_dict(self):
        #json_dict = self.__dict__
        #json_dict["devices"] = list(map(lambda device: device.__dict__, self.devices))
        #return json_dict
        return self.__dict__

    def update_fandom_config(self, fandom_map: dict[str, str], fandom_filter: dict[str, list[str]]) -> None:
        self.fandom_map = fandom_map
        self.fandom_filter = fandom_filter


config = Config(toml.load("./config.toml"))


def get_config() -> Config:
    return config


#This is most likely broken now
def update_config(new_config: Config) -> None:
    global config
    config = new_config
    with open("./test.toml", "w") as f:
        toml.dump(copy(config).to_json_dict(), f)

def reload_fandom_config() -> None:
    new_config = toml.load("./config.toml")
    global config
    config.update_fandom_config(new_config["fandom_map"], new_config["fandom_filter"])
