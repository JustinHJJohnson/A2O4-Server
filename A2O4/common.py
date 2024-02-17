import re

class DB_Series():
    def __init__(self, id: int, title: str, authors: list[str], fandoms: list[str] = []) -> None:
        self.id: int = id
        self.title: str = title
        self.authors: list[str] = authors
        self.fandoms: list[str] = fandoms
    
    def __str__(self):
        return f'DB_Series(id: {self.id}, title: {self.title}, authors: {self.authors}, fandoms: {self.fandoms})'
    
    def __repr__(self):
        return f'DB_Series(id: {self.id}, title: {self.title}, authors: {self.authors}, fandoms: {self.fandoms})'


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


def sanitise_title(title: str) -> str:
    new_title = re.sub(r"/", " ", title)
    return re.sub(r"[^-\w\s.]", "", new_title)