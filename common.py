import re

class DB_Series():
    def __init__(self, id: int, title: str, authors: list[str], fandoms: list[str]) -> None:
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

def sanitise_title(title: str) -> str:
    return re.sub("\/", " ", title)