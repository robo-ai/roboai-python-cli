import pkg_resources


def language_project_path() -> str:
    """
    Auxiliary method to get the default language folder structure.
    """
    return pkg_resources.resource_filename(__name__, "language")


def initial_project_path() -> str:
    """
    Auxiliary method to get the default initial project folder structure.
    """
    return pkg_resources.resource_filename(__name__, "initial_project")
