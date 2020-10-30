import yaml


def load_yaml(path: str) -> dict:
    """
    Loads an existing .yml file into a dictionary.
    :param path: path where the file is stored.
    :return: dictionary with the loaded .yml file.
    """
    with open(path, "r", encoding="UTF-8") as ymlfile:
        return yaml.load(ymlfile, Loader=yaml.FullLoader)


def save_yaml(path: str, yaml_dict: dict) -> None:
    """
    Saves a dictionary into a .yml file.
    :param path: path where the file should be saved.
    :param yaml_dict: dictionary to be saved.
    """
    with open(path, "w", encoding="UTF-8") as ymlfile:
        for key, value in yaml_dict.items():
            yaml.dump(data={key: value}, stream=ymlfile, sort_keys=False)
            ymlfile.write("\n")


def load_md(path: str) -> list:
    """
    Loads an existing file into a list.

    :param path: path where the file is stored

    :return: list with the lines from the file
    """
    with open(path, "r", encoding="UTF-8") as mdfile:
        return mdfile.readlines()


def write_requirements(path: str, req_list: list):

    with open(path, "a+") as f:
        appendEOL = False
        # Move read cursor to the start of file.
        f.seek(0)
        # Check if file is not empty
        data = f.read(100)
        if len(data) > 0:
            appendEOL = True
        # Iterate over each string in the list
        for req in req_list:
            # If file is not empty then append '\n' before first line for
            # other lines always append '\n' before appending line
            if appendEOL:
                f.write("\n")
            else:
                appendEOL = True
            # Append element at the end of file
            f.write(req)
