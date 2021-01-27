import os
from distutils.dir_util import copy_tree
from os.path import join, abspath

import click

from roboai_cli.util.cli import print_info, print_success
from roboai_cli.util.helpers import get_index
from roboai_cli.util.input_output import load_yaml, save_yaml, write_requirements
from roboai_cli.initial_structure.resources_path import language_project_path, initial_project_path


@click.command(
    name="seed",
    help="Create a new ROBO.AI project seedling, "
    "including folder structure and sample files for "
    "all requested languages passed as argument.",
)
@click.argument(
    "languages",
    nargs=-1,
)
@click.option("--path", default=".", type=click.Path(), help="Directory where your project should be initialized.")
@click.option(
    "-ld",
    "--language-detection",
    "language_detection",
    is_flag=True,
    help="Integrates the language detection policy into the bot policies.",
)
@click.option(
    "-cc",
    "--chit-chat",
    "chit_chat",
    is_flag=True,
    help="Integrates the chitchat fallback action \
              into the bot policies. Only available in English.",
)
@click.option(
    "-cr",
    "--coref-resolution",
    "coref_resolution",
    is_flag=True,
    help="Integrates the coreference resolution Spacy model \
              into the bot pipeline. Only available in English.",
)
def command(languages: tuple, path: str, language_detection: bool, chit_chat: bool, coref_resolution: bool) -> None:
    """
    Create a new ROBO.AI project seedling including folder structure and sample files for
    all requested languages passed as argument.

    Args:
        languages: language codes to be included
        path: path where the bot should be created
        language_detection: flag indicating whether language feature should be integrated
        chit_chat: flag indicating whether chit-chat feature should be integrated
        coref_resolution: flag indicating whether coref resolution feature should be integrated
    """
    if len(languages) == 0:
        _inform_language()
        languages = ("en",)

    if path and not os.path.isdir(path):
        _ask_create_path(path)
    # if not args.no_prompt and len(os.listdir(path)) > 0:
    if len(os.listdir(path)) > 0:
        _ask_overwrite(path)

    init_project(path, languages)
    config_setup(path, language_detection, chit_chat, coref_resolution)


def config_setup(path: str, language_detection: bool, chit_chat: bool, coref_resolution: bool) -> None:
    """
    Setup the different options.

    Args:
        path (str): path of the project given by the user.
        language_detection (bool): language_detection flag indicating whether this option is to be included or not.
        chit_chat (bool): chit_chat flag indicating whether this option is to be included or not.
        coref_resolution (bool): coref_resolution flag indicating whether this option is to be included or not.
    """
    if language_detection:
        language_detection_setup(path)
    if chit_chat:
        chit_chat_setup(path)
    if coref_resolution:
        coref_resolution_setup(path)


def coref_resolution_setup(path: str) -> None:
    """
    Setup coreference resolution module into the bot pipeline.

    Args:
        path (str): path of the project given by the user.
    """
    folder_list = [
        join(path, "languages", folder)
        for folder in os.listdir(join(path, "languages"))
        if os.path.isdir(os.path.join(path, "languages", folder))
    ]
    if join(path, "languages", "en") in folder_list:
        en_path = join(path, "languages", "en")
        # add coref resolution to config.yml
        cfg_yaml = load_yaml(join(en_path, "config.yml"))
        components_list = cfg_yaml["pipeline"]
        # remove whitespacetokenizer from the pipeline
        whitespace_idx = get_index(components_list, "WhitespaceTokenizer")
        components_list.pop(whitespace_idx)
        # add spacy model and spacy tokenizer
        components_list.insert(
            0,
            {
                "name": "custom.components.spacy_nlp.\
                                   spacy_tokenizer_neuralcoref.SpacyTokenizerNeuralCoref"
            },
        )
        components_list.insert(
            0,
            {
                "name": "custom.components.spacy_nlp.\
                                   spacy_nlp_neuralcoref.SpacyNLPNeuralCoref",
                "model": "en_neuralcoref",
            },
        )
        cfg_yaml["pipeline"] = components_list
        save_yaml(path=join(en_path, "config.yml"), yaml_dict=cfg_yaml)
        print_success("Coreference resolution model successfully integrated into 'en' bot!")
    # add requirements to requirements.txt
    write_requirements(
        join(path, "requirements.txt"),
        [
            "neuralcoref",
            "en-neuralcoref",
            "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/\
                       download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz",
        ],
    )


def chit_chat_setup(path: str) -> None:
    """
    Setup the cit-chat module.

    Args:
        path (str): path of the project given by the user.
    """
    folder_list = [
        join(path, "languages", folder)
        for folder in os.listdir(join(path, "languages"))
        if os.path.isdir(os.path.join(path, "languages", folder))
    ]
    if join(path, "languages", "en") in folder_list:
        en_path = join(path, "languages", "en")
        # add chitchat fallback action in config.yml
        cfg_yaml = load_yaml(join(en_path, "config.yml"))
        policies_list = cfg_yaml["policies"]
        policies_list.append(
            {
                "name": "FallbackPolicy",
                "nlu_threshold": 0.55,
                "core_threshold": 0.3,
                "fallback_action_name": "action_parlai_fallback",
            }
        )
        cfg_yaml["policies"] = policies_list
        save_yaml(path=join(en_path, "config.yml"), yaml_dict=cfg_yaml)
        # add chitchat fallback action and nedded slots in domain.yml
        domain_yaml = load_yaml(join(en_path, "domain.yml"))
        domain_yaml["actions"] = ["action_parlai_fallback"]
        slots = domain_yaml["slots"]
        slots.update(
            {"parlai_world_created": {"type": "bool", "initial_value": False}, "parlai_world": {"type": "text"}}
        )
        domain_yaml["slots"] = slots
        save_yaml(path=join(en_path, "domain.yml"), yaml_dict=domain_yaml)
        print_success("Chit-chat fallback action successfully integrated into 'en' bot!")


def language_detection_setup(path: str) -> None:

    """
    Setup language detection module.

    Args:
        path (str): path of the project given by the user.
    """

    # include command in config yaml pipeline
    folder_list = [
        join(path, "languages", folder)
        for folder in os.listdir(join(path, "languages"))
        if os.path.isdir(os.path.join(path, "languages", folder))
    ]
    for folder in folder_list:
        # add Language Detection Policy as last Policy in config.yml
        cfg_yaml = load_yaml(join(folder, "config.yml"))
        policies_list = cfg_yaml["policies"]
        policies_list.append(
            {
                "name": "custom.policies.language_detection.lang_change_policy.LangChangePolicy",
                "lang_detect_threshold": 0.8,
                "fallback_action_name": "utter_bot_languages",
                "model_path": "./custom/policies/language_detection/lid.176.ftz",
            }
        )
        cfg_yaml["policies"] = policies_list
        save_yaml(path=join(folder, "config.yml"), yaml_dict=cfg_yaml)
        # add utter example for Labguage Detection Policy fallback in domain.yml
        domain_yaml = load_yaml(join(folder, "domain.yml"))
        responses_dict = domain_yaml["responses"]
        responses_dict["utter_bot_languages"] = [{"text": "Do you want to speak with me in another language?"}]
        domain_yaml["responses"] = responses_dict
        save_yaml(path=join(folder, "domain.yml"), yaml_dict=domain_yaml)
        # add requirements to requirements.txt
    write_requirements(join(path, "requirements.txt"), ["fasttext==0.9.2"])
    print_success("Language detection successfully integrated!")


def init_project(path: str, languages: tuple) -> None:
    """
    Create the initial structure of the project.

    Args:
        path (str): path of the project given by the user
        languages (tuple): requested languages to be included in the initial project
    """
    create_initial_project(path, languages)
    print_success(f"Created project directory at '{abspath(path)}'.")
    # print_train_or_instructions(args, path)


def create_initial_project(path: str, languages: tuple) -> None:
    """
    Copy the initial project structure and add the required languages folder structure to it.

    Args:
        path (str): path of the project given by the user
        languages (tuple): requested languages to be included in the initial project
    """
    copy_tree(initial_project_path(), path)
    add_languages_structure(path, languages)


def add_languages_structure(path: str, languages: tuple) -> None:
    """
    Create the languages folder structure according to the requested languages:

    Args:
        path (str): path of the project given by the user
        languages (tuple): requested languages to be included in the initial project
    """
    for language in languages:
        os.makedirs(join(path, "languages", language), exist_ok=True)
        copy_tree(language_project_path(), join(path, "languages", language))


def _inform_language() -> None:
    """
    Inform the user no languages were passed when executing the seed command.
    """
    print_info("No language was provided. English will be the default.")


def _ask_create_path(path: str) -> None:
    """
    Inform the user the given path is non-existant and if it should be created to proceed with the initial project structure creation.
    In case the answer is negative the user is informed a different path should be chosen.

    Args:
        path (str): path of the project given by the user
    """
    should_create = click.confirm(f"Path '{path}' does not exist 🧐. Create path?")
    if should_create:
        os.makedirs(path)
    else:
        print_success(
            "To proceed with a fresh bot, "
            "please choose a different installation directory and then rerun 'roboai seed'"
        )
        exit(0)


def _ask_overwrite(path: str) -> None:
    """
    Inform the user the given path is not empty and if it still shoudl be used to proceed with the initial project structure creation.
    In case the answer is negative the user is informed a different path should be chosen.

    Args
        path (str): path of the project given by the user
    """
    overwrite = click.confirm(f"Directory '{path}' is not empty. Continue?")
    if not overwrite:
        print_success(
            "To proceed with a fresh bot, "
            "please choose a different installation directory and then rerun 'roboai seed'"
        )
        exit(0)


if __name__ == "__main__":
    command()
