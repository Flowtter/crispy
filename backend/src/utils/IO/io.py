import os
import shutil

from utils.constants import TMP_PATH, IMAGE, CUT


def generate_tmp_folder(overwrite: bool) -> None:
    """
    Generate the tmp directory
    """
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)
    elif overwrite:
        clear_directory(TMP_PATH)
        os.makedirs(TMP_PATH)


def generate_folder_clip(name: str, overwrite: bool = True) -> None:
    """
    Generate the folder clip
    Will generate:
    tmp/{name}/cut
    tmp/{name}/images
    """
    path = os.path.join(TMP_PATH, name)
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(os.path.join(path, CUT))
        os.makedirs(os.path.join(path, IMAGE))
    elif overwrite:
        clear_directory(path)
        generate_folder_clip(name)


def clear_directory(path: str) -> None:
    """
    Clear the given directory
    """
    if os.path.exists(path):
        shutil.rmtree(path)


def generate_clean_name(name: str) -> str:
    """
    Generate the path from the name
    Remove the delim characters from the file name
    Add hash so (hello world) and (hello_world) are different
    """

    def custom_hash(string: str) -> str:
        """
        Generate a hash from the name, same for each session
        """
        h = 0
        for ch in string:
            h = (h * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return str(h)

    init_name = name
    name = name.replace(" ", "__")
    name = name.replace("-", "__")
    name = name.replace("/", "__")
    name = name.replace("\\", "__")

    return name + "-" + custom_hash(init_name)


def remove_extension(name: str) -> str:
    """
    Remove the extension from the file name
    """
    return ".".join(name.split(".")[:-1])


def clean_cuts(folder: str) -> None:
    """
    Clean the cuts folder
    """
    path = os.path.join(TMP_PATH, folder, CUT)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
