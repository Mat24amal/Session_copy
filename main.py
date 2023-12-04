import subprocess
from pathlib import Path

user = "root"
ip = "198.172.15.1"
remote_work_folder_path = Path("...")
local_work_folder_path = Path("...")
ssh_command = f"ssh root@{user}{ip}"


def get_folder_list(work_folder_path: Path, remote: bool) -> set:
    """
    For non remote return set of full paths to the session folders
    For remote return set of session folder names
    """
    result_set = set()

    try:
        if remote:
            # Run the 'ls' command to list folders in the specified path
            result = subprocess.run([ssh_command, 'ls', '-l', str(remote_work_folder_path)], capture_output=True, text=True, check=True)
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
    """
    Creates dictionary from local set
    
    """
    session_dict = dict()
    for session_folder in local_set:
        session_folder_name = session_folder.name
        session_dict[session_folder_name] = session_folder
    return session_dict

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
    for new_session_folder_name in new_session_folder_set:
        new_session_folder = local_session_folder_dict[new_session_folder_name]
        try:
            subprocess.run(["rsync", "-avz", str(new_session_folder), f"{ssh_command}:{remote_work_folder_path}"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error copying {new_session_folder} to {remote_work_folder_path}: {e}")



if __name__ == "__main__":
    main()
