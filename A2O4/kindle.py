import os
import stat
from pathlib import Path

import paramiko

from . import common, config, sqlite


# Stolen from https://stackoverflow.com/questions/4409502/directory-transfers-with-paramiko
class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source: str, target: str) -> None:
        """Uploads the contents of the source directory to the target path. The
        target directory needs to exists. All subdirectories in source are
        created under target.
        """
        target_contents = self.listdir(target)

        if target_contents:
            for item in os.listdir(source):
                if os.path.isfile(os.path.join(source, item)):
                    if item in target_contents:
                        print(f"{item} exists on remote, moving on")
                    else:
                        self.put(os.path.join(source, item), "%s/%s" % (target, item))
                else:
                    self.mkdir("%s/%s" % (target, item), ignore_existing=True)
                    self.put_dir(os.path.join(source, item), "%s/%s" % (target, item))
        else:
            for item in os.listdir(source):
                if os.path.isfile(os.path.join(source, item)):
                    self.put(os.path.join(source, item), "%s/%s" % (target, item))
                else:
                    self.mkdir("%s/%s" % (target, item), ignore_existing=True)
                    self.put_dir(os.path.join(source, item), "%s/%s" % (target, item))

    def remove_dir(self, target: str) -> None:
        for file in self.listdir(target):
            path = os.path.join(target, file)
            if stat.S_ISDIR(self.stat(path).st_mode):
                self.remove_dir(path)
            else:
                self.remove(path)
        self.rmdir(target)

    def exists(self, target: str) -> bool:
        try:
            self.stat(target)
            return True
        except FileNotFoundError:
            return False


def construct_path_for_work(
    work: common.DB_Work, download_folder: str, series_index: int = 0
) -> Path:
    remote_path = Path(download_folder)
    file_name = f"{work.title}.epub"
    if len(work.fandoms) > 1:
        remote_path = remote_path.joinpath("Multiple")
    else:
        remote_path = remote_path.joinpath(work.fandoms[0])
    if work.series_list:
        remote_path = remote_path.joinpath(work.series_list[series_index].title)
        file_name = f"{work.parts[series_index]} - {file_name}"
    remote_path = remote_path.joinpath(file_name)
    return remote_path


def construct_path_for_series(series: common.DB_Series, download_folder: str) -> Path:
    remote_path = Path(download_folder)
    if len(series.fandoms) > 1:
        remote_path = remote_path.joinpath("Multiple")
    else:
        remote_path = remote_path.joinpath(series.fandoms[0])
    remote_path = remote_path.joinpath(series.title)
    return remote_path


def establish_sftp_connection(device: common.Device) -> MySFTPClient:
    transport = paramiko.Transport((device.ip, device.port))
    transport.connect(username=device.username, password=device.password)
    return MySFTPClient.from_transport(transport)


def make_dirs_if_not_exist(
    sftp: MySFTPClient, path: Path, series: bool = False
) -> None:
    dirs_to_create: list[Path] = []
    dirs_to_check: list[Path] = []
    if series:
        dirs_to_check.append(path)
    dirs_to_check.extend(path.parents)
    for dir in dirs_to_check:
        try:
            print(f"checking {dir.as_posix()}")
            sftp.stat(dir.as_posix())
            break
        except FileNotFoundError:
            dirs_to_create.append(dir)

    for _ in range(len(dirs_to_create)):
        dir_to_make = dirs_to_create.pop().as_posix()
        print(f"trying to mkdir {dir_to_make}")
        sftp.mkdir(dir_to_make)


def copy_work(local_path: Path, metadata: common.DB_Work) -> None:
    device_config = config.get_config().devices[0]
    remote_path = construct_path_for_work(metadata, device_config.download_folder)
    sftp = establish_sftp_connection(device_config)
    print(f"local: {local_path.as_posix()}")
    print(f"remote: {remote_path.as_posix()}")
    make_dirs_if_not_exist(sftp, remote_path)
    sftp.put(local_path.as_posix(), remote_path.as_posix())
    sftp.close()
    sqlite.add_work_to_device(metadata.id, device_config.name)


def copy_series(series_to_move: Path, metadata: common.DB_Series) -> None:
    device_config = config.get_config().devices[0]
    remote_path = construct_path_for_series(metadata, device_config.download_folder)
    sftp = establish_sftp_connection(device_config)
    print(f"local: {series_to_move.as_posix()}")
    print(f"remote: {remote_path.as_posix()}")
    make_dirs_if_not_exist(sftp, remote_path, True)
    sftp.put_dir(series_to_move.as_posix(), remote_path.as_posix())
    sftp.close()
    # TODO add series to device sql


def delete_work(metadata: common.DB_Work) -> None:
    device_config = config.get_config().devices[0]
    sftp = establish_sftp_connection(device_config)

    if metadata.series_list:
        for index, _ in enumerate(metadata.series_list):
            path = construct_path_for_work(
                metadata, device_config.download_folder, index
            )
            print(path)
            sftp.remove(path.as_posix())
            sftp.remove_dir(path.with_suffix(".sdr").as_posix())
    else:
        path = construct_path_for_work(metadata, device_config.download_folder)
        print(path)
        if sftp.exists(path.as_posix()):
            sftp.remove(path.as_posix())
        else:
            print("File not found on device, might have already been deleted")
        koreader_metadata_path = path.with_suffix(".sdr").as_posix()
        if device_config.uses_koreader and sftp.exists(koreader_metadata_path):
            sftp.remove_dir(koreader_metadata_path)

    sftp.close()


def delete_series(metadata: common.DB_Series) -> None:
    sftp = establish_sftp_connection(config.get_config().devices[0])
    sftp.remove_dir(
        construct_path_for_series(
            metadata, config.get_config().devices[0].download_folder
        ).as_posix()
    )
    sftp.close()
