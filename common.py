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
        self.port = int(port)
        self.username = username
        self.password = password
        self.loose_download_folder = loose_download_folder
        self.sorted_download_folder = sorted_download_folder

def sanitise_title(title: str) -> str:
    new_title = re.sub(r"/", " ", title)
    return re.sub(r"[^-\w\s.]", "", new_title)