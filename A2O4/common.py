import re
from dataclasses import dataclass, field

@dataclass
class DB_Series():
    id: int
    title: str
    authors: list[str]
    fandoms: list[str] = field(default_factory=list)

@dataclass
class DB_Work():
    id: int
    title: str
    authors: list[str]
    series_list: list[DB_Series]
    parts: list[int]
    fandoms: list[str]

@dataclass
class Device():
    name: str
    ip: str
    port: int
    username: str
    password: str
    download_folder: str
    uses_koreader: bool
    
    def __init__(
        self,
        name: str,
        ip: str,
        port: int,
        username: str,
        password: str,
        download_folder: str,
        uses_KOReader: bool
    ) -> None:
        self.name: str = name
        self.ip: str = ip
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.download_folder: str = download_folder
        self.uses_koreader: bool = uses_KOReader


def sanitise_title(title: str) -> str:
    new_title = re.sub(r"/", " ", title)
    return re.sub(r"[^-\w\s.]", "", new_title)