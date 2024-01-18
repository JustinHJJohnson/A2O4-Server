import AO3T as AO3
#import AO3
import toml
import kindle
import common
import sqlite
from pathlib import Path

config = toml.load(f"./config.toml")

fandom_map: dict[str, str] = {
    "Fallout 4": "Fallout",
    "Fallout (Video Games)": "Fallout",
    "Baldur's Gate (Video Games)": "Baldur's Gate",
    "Cyberpunk 2077 (Video Game)": "Cyberpunk 2077",
    "Persona 5": "Persona",
    "Persona 5 Royal": "Persona",
    "Persona 5 Strikers": "Persona",
    "Persona 4": "Persona",
    "Persona 3": "Persona",
    "persona - Fandom": "Persona",
    "Persona Series": "Persona",
    "逆転裁判 | Gyakuten Saiban | Ace Attorney": "Ace Attorney",
    "大逆転裁判 | Dai Gyakuten Saiban | The Great Ace Attorney Chronicles (Video Games)": "Ace Attorney",
    "NieR: Automata (Video Game)": "NieR"
}

def map_and_filter_fandoms(fandoms: list[str]) -> list[str]:
    new_list = fandoms.copy()
    if ("Baldur's Gate (Video Games)" in new_list and "Dungeons & Dragons (Roleplaying Game)" in new_list):
        new_list.remove("Dungeons & Dragons (Roleplaying Game)")
    new_list = list(set(map(lambda fandom: fandom_map[fandom] if fandom in fandom_map else fandom, new_list)))
    
    return new_list

def download_single_work(work: AO3.Work) -> tuple[Path, common.DB_Work]:
    download_path = Path(config['download_path'])
    authors: list[str] = []
    title = common.sanitise_title(work.title)
    print("Authors are:")
    for author in work.authors:
        print(f"\t{author.username}")
        authors.append(author.username)
    series_list: list[common.DB_Series] = []
    filtered_fandoms = map_and_filter_fandoms(work.metadata['fandoms'])
    print("Series are:")
    for (series, part) in zip(work.series, work.metadata["parts_in_series"]):
        print(f"\t{series.name} part {part}")
        series_authors: list[str] = []
        series.reload()
        for author in series.creators:
            series_authors.append(author.username)
        series_list.append(common.DB_Series(series.id, series.name, series_authors, filtered_fandoms))
    if series_list:
        download_path = download_path.joinpath(series_list[0].title)
        download_path.mkdir(exist_ok=True)
        download_path = download_path.joinpath(f"{work.metadata["parts_in_series"][0]} - {title}.epub")
    else:
        download_path = download_path.joinpath(f"{title}.epub")
    print(f"Unfiltered fandoms are {work.metadata['fandoms']}")
    print(f"Filtered fandoms are {filtered_fandoms}")
    print(f"Downloading {work.title}")
    with open(download_path, "wb") as file:
        file.write(work.download("EPUB"))
        file.close()
    db_work = common.DB_Work(
        work.id,
        title,
        authors,
        work.metadata["parts_in_series"],
        series_list,
        filtered_fandoms
    )
    sqlite.add_work(db_work)
    return (download_path, db_work)

def download_series_and_sort(series: AO3.Series) -> tuple[Path, common.DB_Work]:
    download_path = Path(config['download_path'])
    download_path = download_path.joinpath(series.name)
    download_path.mkdir(exist_ok=True)
    authors: list[str] = []
    fandoms: list[str] = []
    db_works: list[common.DB_Work] = []
    name = common.sanitise_title(series.name)
    for work in series.work_list:
        work.reload()
        authors: list[str] = []
        title = common.sanitise_title(work.title)
        print("Authors are:")
        for author in work.authors:
            print(f"\t{author.username}")
            authors.append(author.username)
        series_list: list[common.DB_Series] = []
        for (work_series, part) in zip(work.series, work.metadata["parts_in_series"]):
            if (work_series.name == series.name): continue
            print(f"\t{series.name} part {part}")
            series_authors: list[str] = []
            work_series.reload()
            for author in series.creators:
                series_authors.append(author.username)
            series_list.append(common.DB_Series(work_series.id, work_series.name, series_authors))
        filtered_fandoms = map_and_filter_fandoms(work.metadata['fandoms'])
        fandoms.extend(filtered_fandoms)
        work_download_path = download_path.joinpath(f"{work.metadata["parts_in_series"][0]} - {title}.epub")
        if (work_download_path.exists()):
            print(f"{work_download_path} exist, skipping")
        else:
            print(f"Downloading {work.title}")
            with open(work_download_path, "wb") as file:
                file.write(work.download("EPUB"))
                file.close()
            db_works.append(
                common.DB_Work(
                    work.id,
                    title,
                    authors,
                    work.metadata["parts_in_series"],
                    series_list,
                    filtered_fandoms
                )
            )
    authors = list(map(lambda author: author.username, series.creators))
    fandoms = map_and_filter_fandoms(fandoms)
    db_series = common.DB_Series(series.id, name, authors, fandoms)
    if db_works:
        sqlite.add_series(db_series, db_works)
    return (download_path, db_series)

def download_work(work_id: int):
    session = AO3.Session(config['ao3_username'], config['ao3_password'])
    work = AO3.Work(work_id, session)
    #download_single_work(work)
    kindle.copy_single_work(*download_single_work(work))

def download_series(series_id: int):
    session = AO3.Session(config['ao3_username'], config['ao3_password'])
    series = AO3.Series(series_id, session)
    #download_series_and_sort(series)
    kindle.copy_series(*download_series_and_sort(series))