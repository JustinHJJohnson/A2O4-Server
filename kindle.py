import toml
import paramiko
import os
import common
import sqlite
from pathlib import Path

# Stolen from https://stackoverflow.com/questions/4409502/directory-transfers-with-paramiko
class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source: str, target: str):
        ''' Uploads the contents of the source directory to the target path. The
          target directory needs to exists. All subdirectories in source are 
          created under target.
        '''
        target_contents = self.listdir(target)

        if target_contents:
            for item in os.listdir(source):
                if os.path.isfile(os.path.join(source, item)):
                    if item in target_contents:
                        print(f"{item} exists on remote, moving on")
                    else:
                        self.put(os.path.join(source, item), '%s/%s' % (target, item))
                else:
                    self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                    self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))
        else:
            for item in os.listdir(source):
                if os.path.isfile(os.path.join(source, item)):
                    self.put(os.path.join(source, item), '%s/%s' % (target, item))
                else:
                    self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                    self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

config = toml.load(f"./config.toml")

def construct_path_for_work(work: common.DB_Work) -> Path:
    remote_path = Path(config['kindle_sorted_download_folder'])
    file_name = f"{work.title}.epub"
    if len(work.fandoms) > 1:
        remote_path = remote_path.joinpath("Multiple/Crossover")
    else:
        remote_path = remote_path.joinpath(work.fandoms[0])
    if work.series_list:
        remote_path = remote_path.joinpath(work.series_list[0].title)
        file_name = f"{work.parts[0]} - {file_name}"
    remote_path = remote_path.joinpath(file_name)
    return remote_path

def construct_path_for_series(series: common.DB_Series) -> Path:
    remote_path = Path(config['kindle_sorted_download_folder'])
    if len(series.fandoms) > 1:
        remote_path = remote_path.joinpath("Multiple/Crossover")
    else:
        remote_path = remote_path.joinpath(series.fandoms[0])
    remote_path = remote_path.joinpath(series.title)
    return remote_path

def establish_sftp_connection() -> MySFTPClient:
    transport = paramiko.Transport(('192.168.2.6', 2222))
    transport.connect(username='root', password='')
    return MySFTPClient.from_transport(transport)

def make_dirs_if_not_exist(sftp: MySFTPClient, path: Path, series: bool = False) -> None:
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

def copy_single_work(local_path: Path, metadata: common.DB_Work) -> None:
    remote_path = construct_path_for_work(metadata)
    sftp = establish_sftp_connection()
    print(f"local: {local_path.as_posix()}")
    print(f"remote: {remote_path.as_posix()}")
    make_dirs_if_not_exist(sftp, remote_path)
    sftp.put(local_path.as_posix(), remote_path.as_posix())
    sftp.close()
    sqlite.add_work_to_device(metadata.id, "Kindle")
    
def copy_series(series_to_move: Path, metadata: common.DB_Series):
    remote_path = construct_path_for_series(metadata)
    sftp = establish_sftp_connection()
    print(f"local: {series_to_move.as_posix()}")
    print(f"remote: {remote_path.as_posix()}")
    make_dirs_if_not_exist(sftp, remote_path, True)
    sftp.put_dir(series_to_move.as_posix(), remote_path.as_posix())
    sftp.close()
