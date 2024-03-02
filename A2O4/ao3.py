from pathlib import Path

import AO3T as AO3

# import AO3
from . import common, config, kindle, sqlite


def map_and_filter_fandoms(fandoms: list[str]) -> list[str]:
    new_list = fandoms.copy()
    new_list = list(
        dict.fromkeys(
            map(
                lambda fandom: config.get_config().fandom_map.get(fandom, fandom),
                new_list,
            )
        )
    )
    for fandom in new_list:
        for fandom_to_remove in config.get_config().fandom_filter.get(fandom, []):
            if fandom_to_remove in new_list:
                new_list.remove(fandom_to_remove)
    return new_list


def download_single_work(work: AO3.Work) -> tuple[Path, common.DB_Work]:
    download_path = Path(config.get_config().download_path)
    authors: list[str] = []
    title = common.sanitise_title(work.title)
    print("Authors are:")
    for author in work.authors:
        print(f"\t{author.username}")
        authors.append(author.username)
    series_list: list[common.DB_Series] = []
    filtered_fandoms = map_and_filter_fandoms(work.metadata["fandoms"])
    print("Series are:")
    for series, part in zip(work.series, work.metadata["parts_in_series"]):
        print(f"\t{series.name} part {part}")
        series_authors: list[str] = []
        series.reload()
        for author in series.creators:
            series_authors.append(author.username)
        series_list.append(
            common.DB_Series(series.id, series.name, series_authors, filtered_fandoms)
        )
    if series_list:
        download_path = download_path.joinpath(series_list[0].title)
        download_path.mkdir(exist_ok=True)
        download_path = download_path.joinpath(
            f"{work.metadata["parts_in_series"][0]} - {title}.epub"
        )
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
        series_list,
        work.metadata["parts_in_series"],
        filtered_fandoms,
    )
    with sqlite.Database() as db:
        db.add_work(db_work)
    return (download_path, db_work)


def download_series_and_sort(series: AO3.Series) -> tuple[Path, common.DB_Series]:
    download_path = Path(config.get_config().download_path)
    download_path = download_path.joinpath(series.name)
    download_path.mkdir(exist_ok=True)
    authors: list[str] = []
    fandoms: list[str] = []
    db_works: list[common.DB_Work] = []
    name = common.sanitise_title(series.name)
    for work in series.work_list:
        work.reload(False)
        work_authors: list[str] = []
        title = common.sanitise_title(work.title)
        print("Authors are:")
        for author in work.authors:
            print(f"\t{author.username}")
            work_authors.append(author.username)
        series_list: list[common.DB_Series] = []
        series_index: int = 0
        for work_series, part in zip(work.series, work.metadata["parts_in_series"]):
            if work_series.name != series.name:
                series_index = series_index + 1
                continue
            print(f"\t{series.name} part {part}")
            series_authors: list[str] = []
            for author in series.creators:
                series_authors.append(author.username)
            series_list.append(
                common.DB_Series(work_series.id, work_series.name, series_authors)
            )
            break
        filtered_fandoms = map_and_filter_fandoms(work.metadata["fandoms"])
        fandoms.extend(filtered_fandoms)
        work_download_path = download_path.joinpath(
            f"{work.metadata["parts_in_series"][series_index]} - {title}.epub"
        )
        if work_download_path.exists():
            print(f"{work_download_path} exist, skipping")
        else:
            print(f"Downloading {work.title}")
            work.load_chapters()
            with open(work_download_path, "wb") as file:
                file.write(work.download("EPUB"))
                file.close()
            db_works.append(
                common.DB_Work(
                    work.id,
                    title,
                    work_authors,
                    series_list,
                    work.metadata["parts_in_series"],
                    filtered_fandoms,
                )
            )
    authors = list(map(lambda author: author.username, series.creators))
    fandoms = map_and_filter_fandoms(fandoms)
    db_series = common.DB_Series(series.id, name, authors, fandoms)
    if db_works:
        with sqlite.Database() as db:
            db.add_series(db_series, db_works)
    return (download_path, db_series)


def download_work(id: int) -> common.DB_Work:
    session = AO3.Session(
        config.get_config().ao3_username, config.get_config().ao3_password
    )
    work = AO3.Work(id, session, load_chapters=False)
    db_work = download_single_work(work)
    kindle.copy_work(*db_work)
    return db_work[1]


def download_series(id: int) -> common.DB_Series:
    session = AO3.Session(
        config.get_config().ao3_username, config.get_config().ao3_password
    )
    series = AO3.Series(id, session)
    db_series = download_series_and_sort(series)
    kindle.copy_series(*db_series)
    return db_series[1]


# TODO think about these functions, wasteful to get the work/series from the database twice
def delete_work(id: int) -> None:
    with sqlite.Database() as db:
        db.delete_work(id)
        kindle.delete_work(db.get_work(id))
    return


def delete_series(id: int) -> None:
    with sqlite.Database() as db:
        db.delete_series(id)
        kindle.delete_series(db.get_series(id))
    return
