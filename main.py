import logging
import subprocess
from pathlib import Path, PurePosixPath, WindowsPath

import yaml


def get_folder_list(
    work_folder_path: Path | PurePosixPath | WindowsPath,
    remote: bool,
    ssh_user: str | None = None,
    ssh_host: str | None = None,
    ssh_port: int | None = None,
) -> set:
    """
    For non remote return set of full paths as string to the session folders
    For remote return set of session folder names
    """
    result_set = set()

    try:
        if type(work_folder_path) is PurePosixPath:
            # Run the 'ls' command to list folders in the specified path
            command = ["ssh", f"{ssh_user}@{ssh_host}", "ls", "-l", str(work_folder_path)]
            if ssh_port:
                command.insert(1, "-p")
                command.insert(2, str(ssh_port))

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )

            # get folder names from the output
            folders = [line.split()[-1] for line in result.stdout.split("\n") if line.startswith("d")]
            # add folder names to set
            result_set.update(folders)

        elif type(work_folder_path) is WindowsPath or type(work_folder_path) is Path:
            result_set.update(
                [str(session_folder) for session_folder in work_folder_path.iterdir() if session_folder.is_dir()]
            )

        else:
            raise Exception(f"Unknown type of work_folder_path: {type(work_folder_path)}")

        return result_set
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error getting folder list from {work_folder_path}: {e}")

    logging.info(f"Got folder list from {work_folder_path}")


def create_dict_from_local_set(local_set: set) -> dict:
    """
    Creates dictionary from local set

    """
    session_dict = dict()
    for session_folder in local_set:
        session_folder_path = Path(session_folder)
        session_folder_name = session_folder_path.name
        session_dict[session_folder_name] = session_folder_path
    return session_dict
    logging.info("Created session dict")


def main(
    local_work_folder_path: Path,
    remote_work_folder_path: PurePosixPath,
    ssh_user: str,
    ssh_host: str,
    ssh_port: int | None = None,
):
    # get both sets and find the one that are not in remote
    remote_session_folder_set = get_folder_list(
        remote_work_folder_path, remote=True, ssh_user=user, ssh_host=ip, ssh_port=ssh_port
    )
    local_session_folder_set = get_folder_list(local_work_folder_path, remote=False)
    logging.info(f"Compering folder in {local_work_folder_path} with {remote_work_folder_path}")

    # create dict from local set
    local_session_folder_dict = create_dict_from_local_set(local_session_folder_set)
    local_folder_session_name_set = set(local_session_folder_dict.keys())

    # find the difference between local and remote
    new_session_folder_set = local_folder_session_name_set - remote_session_folder_set
    logging.info(f"Found {len(new_session_folder_set)} new folders")

    # copy new folders to remote
    for new_session_folder_name in new_session_folder_set:
        new_session_folder = local_session_folder_dict[new_session_folder_name]
        try:
            command = ["scp", "-r", str(new_session_folder), f"{ssh_user}@{ssh_host}:{remote_work_folder_path}/"]
            if ssh_port:
                command.insert(1, "-P")
                command.insert(2, str(ssh_port))
            subprocess.run(
                command,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error copying {new_session_folder} to {remote_work_folder_path}: {e}")
    logging.info(f"Copied {len(new_session_folder_set)} new folders to {remote_work_folder_path}")


def read_config(config_file_path: Path) -> dict:
    """
    Reads config file and returns config as dict
    """
    try:
        with open(config_file_path, "r") as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        raise Exception(f"Error reading config file {config_file_path}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config_file_path = Path("config.yml")
    config = read_config(config_file_path)
    user = config.get("user")
    ip = config.get("ip")
    port = config.get("port")
    remote_work_folder = config.get("remote_work_folder")
    local_work_folder = config.get("local_work_folder")
    if not user or not ip or not remote_work_folder or not local_work_folder:
        raise Exception("Missing config values")

    main(Path(local_work_folder), PurePosixPath(remote_work_folder), user, ip, port)
# w
