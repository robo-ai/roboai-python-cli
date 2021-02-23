import json
from os import listdir, system
from os.path import abspath, join, exists, isdir, basename
import tempfile
import shutil
import yaml
import ast

import click
import pandas as pd

from roboai_cli.util.cli import print_info


@click.command(name="data", help="Utility command to split, export and import data.")
@click.argument("utility", nargs=1)
@click.argument("option", nargs=1)
@click.argument("languages", nargs=-1)
@click.option("--input-path", default=".", type=click.Path(), help="Optional input path")
@click.option("--output-path", default=".", type=click.Path(), help="Optional output path")
def command(utility: tuple, option: tuple, languages: tuple, input_path: str, output_path: str):
    """
    Utility command to split, export and import data.

    Args:
        utility (tuple): can be 'split' to split data, 'export' to export data and 'import' to import data
        option (tuple): can be 'nlu', 'domain' or 'all'. It depends on the utility argument.
        languages (tuple): bot language to split, export or import data from.
        input_path (str): optional input path where files are stored.
        output_path (str): optional output path where files are to be stored.
    """

    if option == "export":
        path = input_path
    elif option == "import":
        path = output_path
    else:
        path = "."  # TODO not sure ...

    if len(languages) == 0:
        if exists(join(abspath(path), "languages")):
            bot_dir = get_all_languages(path=abspath(path), languages=languages)
            multi_language_bot = True
        else:
            bot_dir = [abspath(".")]
            multi_language_bot = False
    else:
        bot_dir = get_all_languages(path=abspath(path), languages=languages)
        multi_language_bot = True

    if utility == "split":
        if option == "nlu":
            split_nlu(bot_dir, multi_language_bot)
        else:
            print("Please select a valid option.")
            exit(0)
    elif utility == "export":
        if option == "all":
            export_all(bot_dir, output_path)
        if option == "nlu":
            export_nlu(bot_dir, output_path)
        elif option == "domain":
            export_domain(bot_dir, output_path)
        else:
            print("Please select a valid element to export. It can be either 'nlu', 'domain' or 'all' to export both.")
    elif utility == "import":
        if option == "all":
            import_all(output_path, bot_dir, multi_language_bot)
        elif option == "nlu":
            import_nlu(output_path, bot_dir, multi_language_bot)
        elif option == "domain":
            import_domain(output_path, bot_dir, multi_language_bot)
        else:
            print("Please select a valid element to import. It can be either 'nlu', 'domain' or 'all' to import both.")
    else:
        print("Please select a valid utility option.")
        exit(0)


def split_nlu(bot_dir: list, multi_language_bot: bool):
    """
    Run rasa command to split the nlu file

    Args:
        bot_dir (list): list of paths respective to each bot
        multi_language_bot (bool): flag indicating whether the bot is multi language or not
    """
    for language in bot_dir:
        if multi_language_bot:
            system(f"rasa data split nlu -u {join(language, 'data')} --out {join(language, 'train_test_split')}")
        else:
            system(f"rasa data split nlu -u {join(language, 'data')}")


def convert_nlu_to_df(input_path: str) -> pd.DataFrame:
    """
    Convert nlu file from markdown to a pandas dataframe.
    Intents and respective examples are kept. Regex features, lookup tables and entity synonyms are discarded.

    Args:
        input_path (str): input path to read the nlu file from

    Returns:
        pd.DataFrame: pandas dataframe containing the nlu content
    """
    tmp_dir = tempfile.mkdtemp()
    tmp_file = "nlu.json"

    system(f"rasa data convert nlu --data {join(input_path, 'data', 'nlu.md')} \
           -f json --out {join(tmp_dir, tmp_file)}")

    with open(join(tmp_dir, tmp_file), "r", encoding="utf-8") as f:
        nlu_json = json.load(f)

    shutil.rmtree(tmp_dir)

    nlu_df = pd.DataFrame(nlu_json["rasa_nlu_data"]["common_examples"])[["intent", "text"]]

    return nlu_df


def convert_domain_to_df(input_path: str) -> pd.DataFrame:
    """
    Convert domain file to a pandas dataframe.
    Responses are kept, all other information like slots, list of intents, etc are discarded.

    Args:
        input_path (str): input path to read the domain file from

    Returns:
        pd.DataFrame: pandas dataframe containing the domain responses
    """
    with open(join(input_path, "domain.yml")) as f:
        domain = yaml.load(f, Loader=yaml.FullLoader)

    responses = domain.get("responses", None)
    if not responses:
        print("No responses were found in the domain file.")
        exit(0)

    response_df = pd.DataFrame()
    i = 0
    for response_key, response_value in responses.items():
        for option in response_value:
            for answer in option["custom"]["answers"]:
                response_df.loc[i, "response_name"] = response_key
                if answer["type"] == "html":
                    response_df.loc[i, "html"] = answer["text"]
                elif answer["type"] == "text":
                    response_df.loc[i, "text"] = answer["text"]
                elif answer["type"] == "ssml":
                    response_df.loc[i, "ssml"] = answer["ssml"]
                elif answer["type"] == "hints":
                    response_df.loc[i, "hints"] = str(answer["options"])
                elif answer["type"] == "multichoice":
                    response_df.loc[i, "multichoice"] = str(answer["options"])
                else:
                    response_df.loc[i, answer["type"]] = str(answer)
            i += 1

    return response_df


def export_nlu(bot_dir: list, output_path: str):
    """
    Export nlu dataframe to a given output path.

    Args:
        bot_dir (list): list of paths respective to each bot
        output_path (str): output path where the nlu should be stored
    """
    for language in bot_dir:
        nlu_df = convert_nlu_to_df(language)
        lang = basename(language) if basename(language) != "bot" else "bot"
        nlu_df.to_excel(join(output_path, "nlu-" + lang + ".xlsx"), index=False, sheet_name="NLU")


def export_domain(bot_dir: list, output_path: str):
    """
    Export domain dataframe to a given output path.

    Args:
        bot_dir (list): list of paths respective to each bot
        output_path (str): output path where the domain should be stored
    """
    for language in bot_dir:
        domain_df = convert_domain_to_df(language)
        lang = basename(language) if basename(language) != "bot" else "bot"
        domain_df.to_excel(join(output_path, "domain-" + lang + ".xlsx"), index=False, sheet_name="Domain")


def export_all(bot_dir: list, output_path: str):
    """
    Export both nlu and domain to one single output file.

    Args:
        bot_dir (list): list of paths respective to each bot
        output_path (str): output path where both the nlu and domain should be stored
    """
    for language in bot_dir:
        lang = basename(language) if basename(language) != "bot" else "bot"
        with pd.ExcelWriter(join(output_path, lang + "-content.xlsx"), engine="xlsxwriter") as xlsx_writer:
            domain_df = convert_domain_to_df(language)
            domain_df.to_excel(excel_writer=xlsx_writer, index=False, sheet_name="Domain")
            nlu_df = convert_nlu_to_df(language)
            nlu_df.to_excel(excel_writer=xlsx_writer, index=False, sheet_name="NLU")


def import_nlu(input_path: str, output_path: str):
    """
    Import nlu file back to markdown

    Args:
        input_path (str): path where to read nlu file from
        output_path (str): path to store converted nlu
    """
    try:
        nlu_df = pd.read_excel(input_path, sheet_name="NLU")
    except Exception:
        print("It was not possible to read the file you provided. Make sure the file exists and it contains an NLU tab.")

    nlu_dict = convert_nlu_df_to_dict(nlu_df)

    for intent, examples in nlu_dict.items():
        with open(join(output_path, "nlu_converted.md"), "+a") as f:
            f.write(f"## intent:{intent}\n")
            for example in examples:
                f.write(f"- {example}\n")
            f.write("\n")


def import_domain(input_path: str, output_path: str):
    """
    Import responses back to yaml

    Args:
        input_path (str): path where to read the responses file from
        output_path (str): path to store converted responses
    """
    try:
        response_df = pd.read_excel(input_path, sheet_name="Domain")
    except Exception:
        print("It was not possible to read the file you provided. Make sure the file exists and it contains a Domain tab.")

    response_dict = convert_response_df_to_dict(response_df)

    with open(join(output_path, "responses_converted.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump(response_dict, stream=outfile, allow_unicode=True)


def import_all():
    pass


def convert_response_df_to_dict(response_df: pd.DataFrame) -> dict:
    """
    Convert responses dataframe to dict

    Args:
        response_df (pd.DataFrame): dataframe containing the responses

    Returns:
        dict: dictionary containing the reponses
    """
    column_names = response_df.columns.tolist()[1:]
    domain_dict = {k: [] for k in response_df["response_name"].unique().tolist()}
    for i, row in response_df.iterrows():
        current_response = row["response_name"]
        print(current_response)
        custom_dict = {"custom": {"answers": []}}

        for col in column_names:
            if pd.notna(row[col]):
                if col == "html":
                    custom_dict["custom"]["answers"].append({"type": "html", "text": row["html"]})
                elif col == "text":
                    custom_dict["custom"]["answers"].append({"type": "text", "text": row["text"]})
                elif col == "ssml":
                    custom_dict["custom"]["answers"].append({"type": "ssml", "ssml": row["ssml"]})
                elif col == "hints":
                    custom_dict["custom"]["answers"].append({"type": "hints",
                                                            "options": ast.literal_eval(row["hints"])})
                elif col == "multichoice":
                    custom_dict["custom"]["answers"].append({"type": "multichoice",
                                                            "options": ast.literal_eval(row["multichoice"])})
                else:
                    custom_dict["custom"]["answers"].append(ast.literal_eval(row[col]))

        domain_dict[row["response_name"]].append(custom_dict)

    return domain_dict


def convert_nlu_df_to_dict(nlu_df: pd.DataFrame) -> dict:
    """
    Convert nlu dataframe to dict

    Args:
        nlu_df (pd.DataFrame): dataframe containing the nlu

    Returns:
        dict: dictionary containing the nlu
    """
    intents_dict = {}
    unique_intents = nlu_df["intent"].unique().tolist()
    for intent in unique_intents:
        examples = nlu_df[nlu_df["intent"] == intent]["text"].tolist()
        intents_dict[intent] = examples

    return intents_dict


def get_all_languages(path: str, languages: tuple) -> list:
    if len(languages) == 0:
        _inform_language()
        languages_paths = [
            join(path, "languages", folder)
            for folder in listdir(join(path, "languages"))
            if isdir(join(path, "languages", folder))
        ]
    else:
        languages_paths = [
            join(path, "languages", folder)
            for folder in listdir(join(path, "languages"))
            if isdir(join(path, "languages", folder)) and folder in languages
        ]
    return languages_paths


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the data command.
    """
    print_info(
        "No language was provided but a multi-language bot was detected. "
        "Will gather all available languages inside provided bot folder.\n"
    )


if __name__ == "__main__":
    command()
