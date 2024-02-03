import re

class DB_Series():
    def __init__(self, id: int, title: str, authors: list[str], fandoms: list[str] = []) -> None:
        self.id: int = id
        self.title: str = title
        self.authors: list[str] = authors
        self.fandoms: list[str] = fandoms

class DB_Work():
    def __init__(self, id: int, title: str, authors: list[str], parts: list[int], series_list: list[DB_Series], fandoms: list[str]) -> None:
        self.id: int = id
        self.title: str = title
        self.authors: list[str] = authors
        self.series_list: list[DB_Series] = series_list
        self.parts: list[int] = parts
        self.fandoms: list[str] = fandoms

class Device():
    def __init__(self, name: str, ip: str, port: int, username: str, password: str, loose_download_folder: str, sorted_download_folder: str) -> None:
        self.name: str = name
        self.ip: str = ip
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.loose_download_folder: str = loose_download_folder
        self.sorted_download_folder: str = sorted_download_folder
        
    def __str__(self):
        return f'Device(name: {self.name}, ip: {self.ip}, port: {self.port}, username: {self.username}, password: {self.password}, loose_download_folder: {self.loose_download_folder}, sorted_download_folder: {self.sorted_download_folder})'
    
    def __repr__(self):
        return f'Device(name: {self.name}, ip: {self.ip}, port: {self.port}, username: {self.username}, password: {self.password}, loose_download_folder: {self.loose_download_folder}, sorted_download_folder: {self.sorted_download_folder})'

class Config():
    def __init__(self, config: dict) -> None:
        print(config['devices'])
        self.download_path: str = config["download_path"]
        self.ao3_username: str = config["ao3_username"]
        self.ao3_password: str = config["ao3_password"]
        self.devices: list[Device] = list(map(lambda device: Device(**device), config['devices']))
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


def sanitise_title(title: str) -> str:
    new_title = re.sub(r"/", " ", title)
    return re.sub(r"[^-\w\s.]", "", new_title)