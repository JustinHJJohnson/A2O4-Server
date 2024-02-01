import re

class DB_Series():
    def __init__(self, id: int, title: str, authors: list[str], fandoms: list[str] = []) -> None:
        self.id = id
        self.title = title
        self.authors = authors
        self.fandoms = fandoms

class DB_Work():
    def __init__(self, id: int, title: str, authors: list[str], parts: list[int], series_list: list[DB_Series], fandoms: list[str]) -> None:
        self.id = id
        self.title = title
        self.authors = authors
        self.series_list = series_list
        self.parts = parts
        self.fandoms = fandoms

class Device():
    def __init__(self, name: str, ip: str, port: int, username: str, password: str, loose_download_folder: str, sorted_download_folder: str) -> None:
        self.name = name
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.loose_download_folder = loose_download_folder
        self.sorted_download_folder = sorted_download_folder

class Config():
    def __init__(self, config: dict) -> None:
        self.download_path: str = config["download_path"]
        self.ao3_username: str = config["ao3_username"]
        self.ao3_password: str = config["ao3_password"]
        self.devices: list[Device] = list(map(lambda device: Device(*device), config['devices']))
        self.fandom_map: dict[str, str] = config['fandom_map']
        self.fandom_filter: dict[str, list[str]] = config['fandom_filter']


def sanitise_title(title: str) -> str:
    new_title = re.sub(r"/", " ", title)
    return re.sub(r"[^-\w\s.]", "", new_title)