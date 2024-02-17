import toml
from . import common

class Config():
    def __init__(self, config: dict) -> None:
        self.download_path: str = config["download_path"]
        self.ao3_username: str = config["ao3_username"]
        self.ao3_password: str = config["ao3_password"]
        self.devices: list[common.Device] = list(map(lambda device: common.Device(**device), config['devices']))
        self.fandom_map: dict[str, str] = config['fandom_map']
        self.fandom_filter: dict[str, list[str]] = config['fandom_filter']
    
    def __str__(self):
        return f"""
            download_path: {self.download_path}
            ao3_username: {self.ao3_username}
            ao3_password: {self.ao3_password}
            devices: {self.devices}
            fandom_map: {self.fandom_map}
            fandom_filter: {self.fandom_filter}
        """
    
    def __repr__(self):
        return f"""
            download_path: {self.download_path}
            ao3_username: {self.ao3_username}
            ao3_password: {self.ao3_password}
            devices: {self.devices}
            fandom_map: {self.fandom_map}
            fandom_filter: {self.fandom_filter}
        """
    
    def to_json_dict(self):
        json_dict = self.__dict__
        json_dict["devices"] = list(map(lambda device: device.__dict__, self.devices))
        return json_dict


print("loading config")
config = Config(toml.load(f"./config.toml"))
print("config loaded")
    
def get_config() -> Config:
    return config

def update_config(new_config: Config) -> None:
    global config 
    config = new_config
    f = open(f'./test.toml', 'w')
    toml.dump(config.to_json_dict(), f)
    f.close()