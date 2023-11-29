import subprocess
from pathlib import Path 

user = "root"
ip = "198.172.15.1"
remote_work_folder_path = Path("...")
local_work_folder_path = Path("...")
ssh_command = f"ssh root@{user}{ip}"


def get_folder_list(work_folder_path: Path, remote: bool) -> set: #insted of . use your path
    """
    For non remote return set of full paths to the session folders
    For remote return set of session folder names
    """
    result_set = set()

    try:
        if remote:
            # Run the 'ls' command to list folders in the specified path
            result = subprocess.run([ssh_command, 'ls', '-l', str(work_folder_path)], capture_output=True, text=True, check=True)
            # get folder names from the output
            folders = [line.split()[-1] for line in result.stdout.split('\n') if line.startswith('d')]
            # add folder names to set
            result_set.update(folders)

        else:
            for username_folder in work_folder_path.iterdir():
                if username_folder.is_dir():
                    for session_folder in username_folder.iterdir():
                        if session_folder.is_dir():
                            result_set.add(session_folder)

        return result_set
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def create_dict_from_local_set(local_set: set) -> dict:
    session_dict = dict()
    for session_folder in local_set:
        session_folder_name = session_folder.name
        session_dict[session_folder_name] = session_folder
    return session_dict


def copy_folders_to_cluser():
    pass


def main():
    # get both sets and find the one that are not in remote
    remote_session_folder_set = get_folder_list(remote_work_folder_path, remote=True)
    local_session_folder_set = get_folder_list(local_work_folder_path, remote=False)

    # create dict from local set
    local_session_folder_dict = create_dict_from_local_set(local_session_folder_set)
    local_folder_session_name_set = set(local_session_folder_dict.keys())

    # find the difference between local and remote
    new_session_folder_set = local_folder_session_name_set - remote_session_folder_set

    # copy new folders to remote


if __name__ == "__main__":
    main()
