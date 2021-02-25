import json
import os
import random
from collections import defaultdict
from os import listdir, mkdir, makedirs
from os.path import abspath, basename, dirname, exists, isfile, join
from re import search, sub
from datetime import datetime

import click
import pandas as pd

from roboai_cli.util.cli import print_error, print_info
from roboai_cli.util.input_output import load_md, load_yaml
from roboai_cli.util.helpers import clean_intents, user_proceed


@click.command(name="test", help="Test Rasa models for the required bots.")
@click.argument("languages", nargs=-1,)
@click.option("--cross-validation", is_flag=True, default=False, help="Evaluates model in cross-validation mode.")
@click.option("--folds", "-f", "folds", type=int, default=3, help="Number of folds to be applied in cross-validation mode.")
@click.option("--test-data-path", default=None, type=click.Path(), help="Path to where test data is stored.")
def command(languages: tuple, cross_validation: bool, folds: int, test_data_path: str):
    """
    Test a Rasa bot.

    Args:
        languages (tuple): languages (bots) to be tested. If no language is passed
                           it checks if the current bot is a multi-language bot. If so
                           all bots will be tested. Otherwise the single-language bot will
                           be tested.
        cross_validation (bool): Evaluates model in cross-validation mode.
        folds (int): Number of folds to be applied in cross-validation mode.
        test_data_path (str): Path to testing data in case you have split it before.
    """
    if len(languages) == 0:
        if exists(join(abspath("."), "languages")):
            # multi-language bot
            bot_dir = get_all_languages(path=abspath("."), languages=languages)
            multi_language_bot = True
        else:
            # single-language bot
            bot_dir = [abspath(".")]
            multi_language_bot = False
    else:
        multi_language_bot = True
        bot_dir = get_all_languages(path=abspath("."), languages=languages)
    test(bot_dir, multi_language_bot, cross_validation, folds, test_data_path)


def test(languages_path: list, multi_language_bot: bool, cross_validation: bool, folds: int, test_data_path: str) -> None:
    timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
    for language in languages_path:
        makedirs(join(language, "results", timestamp), exist_ok=True)
        lang = basename(language) if basename(language) != "bot" else "the"
        print_info(f"Starting test process for {lang} bot")
        # Check if tests folder exists
        if exists(join(language, "tests")):
            # Check if tests folder contains any file
            if any(
                isfile(join(language, "tests", i))
                for i in listdir(join(language, "tests"))
            ):
                # Check if intents are already covered in the existing test files
                # If there are intents left to be tested, the user is prompted
                # with an option to continue testing
                if check_covered_intents(language):
                    test_bot(language, cross_validation, folds, test_data_path, timestamp)
                else:
                    continue
            # If tests folder is empty, generate a test stories file
            else:
                generate_conversation_md_from_stories(
                    language, multi_language_bot
                )
                if user_proceed(
                    "Test stories have been generated. Continue testing?\n"
                ):
                    test_bot(language, cross_validation, folds, test_data_path, timestamp)
                else:
                    continue
        # If tests folder doesn't exist, create it and generate a test stories file
        else:
            generate_conversation_md_from_stories(language, multi_language_bot)
            if user_proceed(
                "Test stories have been generated. Continue testing?\n"
            ):
                test_bot(language, cross_validation, folds, test_data_path, timestamp)
            else:
                continue
        format_results(language, timestamp)
        print_info(f"Finished testing {lang} bot")


def test_bot(language: str, cross_validation: bool, folds: int, test_data_path: str, timestamp: str):
    if cross_validation:
        os.system(
            f"rasa test --model {join(language, 'models')} \
                --nlu {join(language, 'data') if not test_data_path else join(language, test_data_path)} \
                --cross-validation -f {folds} --config {join(language, 'config.yml')} \
                --stories {join(language, 'tests')} --out {join(language, 'results', timestamp)}"
        )
    else:
        os.system(
            f"rasa test --model {join(language, 'models')} \
                --nlu {join(language, 'data') if not test_data_path else join(language, test_data_path)} \
                --stories {join(language, 'tests')} --out {join(language, 'results', timestamp)}"
        )


def check_covered_intents(language_path: str) -> bool:
    intents = load_yaml(join(language_path, "domain.yml")).get("intents", None)
    if intents is None:
        print_error("No intents were found.\n")
        exit(0)
    else:
        intents = clean_intents(intents)
        for filename in listdir(join(language_path, "tests")):
            if filename.endswith(".md"):
                lines = load_md(join(language_path, "tests", filename))
                for line in lines:
                    for intent in intents:
                        if intent in line:
                            intents.remove(intent)
                            break
        if intents:
            print(
                "The following intents are not covered in your test stories:"
            )
            print(*intents, sep="\n")
            should_test = user_proceed("Continue testing?\n")
        else:
            should_test = True
        return should_test


def get_intent_example(intent: str, nlu) -> str:
    examples = []
    copy = False
    comment = False
    for line in nlu:
        if line.startswith("##") and search(r"\b" + intent + r"\b", line):
            if comment is False:
                copy = True
        elif line.startswith("##") and not search(
            r"\b" + intent + r"\b", line
        ):
            if comment is False:
                copy = False
        elif line.strip().startswith("<!--") and line.strip().endswith("-->"):
            comment = False
        elif line.startswith("<!--") or line.strip().startswith("<!------------------"):
            comment = True
        elif line.endswith("-->\n") or line.strip().endswith("------------------->"):
            comment = False
        elif copy:
            # keep entities
            examples.append(line.replace("-", "", 1).strip())
            # remove entities
            # examples.append(
            #     sub(r"\{[^)]*\}", "", line)
            #     .replace("[", "")
            #     .replace("]", "")
            #     .replace("-", "", 1)
            #     .strip()
            # )
    examples = [i for i in examples if i]
    if examples:
        return random.choice(examples)
    else:
        return ""


def generate_conversation_md_from_stories(
    path_to_language: str, multi_language_bot: bool
):
    """Generates test stories based on the stories.md file.
    Complex stories are generated because they're copied from the original stories.md file

    Args:
        path_to_language (str): path_to_language (str): path to language folder.
            If it's a single-language bot this will be the bot root's folder.
        multi_language_bot (bool): flag indicating whether the bot is single or multi language
    """
    if multi_language_bot:
        stories_path = dirname(join(path_to_language))
    else:
        stories_path = join(path_to_language, "data")

    all_stories = []
    for filename in listdir(stories_path):
        if isfile(join(stories_path, filename)):
            if "stories" in filename:
                stories = load_md(join(stories_path, filename))
                all_stories.append(stories)
    all_stories = [item for sublist in all_stories for item in sublist]
    all_nlu = []
    for filename in listdir(join(path_to_language, "data")):
        if isfile(join(path_to_language, "data", filename)):
            if "stories" not in filename:
                nlu = load_md(join(path_to_language, "data", filename))
                all_nlu.append(nlu)
    all_nlu = [item for sublist in all_nlu for item in sublist]
    output_path = join(path_to_language, "tests", "conversation_tests.md")
    if not exists(join(path_to_language, "tests")):
        mkdir(join(path_to_language, "tests"))
    with open(output_path, "w", encoding="utf-8") as out_f:
        for line in stories:
            if line.startswith("*"):
                intent = (
                    sub(r"\{[^)]*\}", "", line)
                    .replace("[", "")
                    .replace("]", "")
                    .replace("*", "", 1)
                    .strip()
                )
                if " or " in line.lower():
                    first_intent = intent.split()[0]
                    out_f.write(
                        f"* {first_intent}: {get_intent_example(first_intent, all_nlu)}\n"
                    )
                elif "form:" in line.lower():
                    intent_in_form = intent.split()[1]
                    out_f.write(
                        f"* form: {intent_in_form}: {get_intent_example(intent_in_form, all_nlu)}\n"
                    )
                else:
                    intent = (
                        sub(r"\{[^)]*\}", "", line)
                        .replace("[", "")
                        .replace("]", "")
                        .replace("*", "", 1)
                        .strip()
                    )
                    out_f.write(
                        f"* {intent}: {get_intent_example(intent, all_nlu)}\n"
                    )
            else:
                out_f.write(line)


def generate_conversation_md_from_domain(path_to_language: str):
    """Generates test stories based on the intents available in the domain.
    Complex stories are not generated.

    Args:
        path_to_language (str): path to language folder.
        If it's a single-language bot this will be the bot root's folder.
    """
    domain = load_yaml(join(path_to_language, "domain.yml"))
    intents_list = domain.get("intents", None)
    all_nlu = []
    for filename in listdir(join(path_to_language, "data")):
        if isfile(join(path_to_language, "data", filename)):
            if "stories" not in filename:
                nlu = load_md(join(path_to_language, "data", filename))
                all_nlu.append(nlu)

    all_nlu = [item for sublist in all_nlu for item in sublist]
    if not intents_list:
        print_error("No intents were found.")
        exit(0)
    elif intents_list:
        output_path = join(path_to_language, "tests", "conversation_tests.md")
        if not exists(join(path_to_language, "tests")):
            mkdir(join(path_to_language, "tests"))
        with open(output_path, "w", encoding="utf-8") as out_f:
            for intent in intents_list:
                out_f.write(f"## {intent}\n")
                out_f.write(
                    f"* {intent}: {get_intent_example(intent, all_nlu)}\n"
                )
                out_f.write(f"  - utter_{intent}\n")
                out_f.write("\n")


def format_results(language_path: str, timestamp: str):
    """
    Format the results output by Rasa. This includes:
        - confusion list stating how many times two intents are being confused
        - misclassified intents: the same as above but it shows the specific utters
        - statistics table: containing metrics like accuracy, precision, etc.

    Args:
        language_path (str): path to language folder.
        timestamp (str): timestamp of when the test is run.
    """
    try:
        confusion_list = confusion_table_df(language_path, timestamp)
        misclassified_intents = misclassified_intents_df(language_path, timestamp)
        statistics_table = stats_table(language_path, timestamp)

        with pd.ExcelWriter(
            join(language_path, "results", timestamp, "intent_details.xlsx"),
            engine="xlsxwriter",
        ) as xlsx_writer:
            confusion_list.to_excel(
                excel_writer=xlsx_writer, sheet_name="Confusion Table", index=False
            )
            worksheet = xlsx_writer.sheets["Confusion Table"]
            for i, col in enumerate(confusion_list.columns):
                column_len = max(
                    confusion_list[col].astype(str).str.len().max(), len(col) + 2
                )
                worksheet.set_column(i, i, column_len)

            misclassified_intents.to_excel(
                excel_writer=xlsx_writer, sheet_name="Misclassified Intents", index=False
            )
            worksheet = xlsx_writer.sheets["Misclassified Intents"]
            for i, col in enumerate(misclassified_intents.columns):
                column_len = max(
                    misclassified_intents[col].astype(str).str.len().max(),
                    len(col) + 2,
                )
                worksheet.set_column(i, i, column_len)

            statistics_table.to_excel(
                excel_writer=xlsx_writer, sheet_name="Intent Statistics", index=False
            )
            worksheet = xlsx_writer.sheets["Intent Statistics"]
            for i, col in enumerate(statistics_table.columns):
                column_len = max(
                    statistics_table[col].astype(str).str.len().max(),
                    len(col) + 2,
                )
                worksheet.set_column(i, i, column_len)
    except Exception:
        print_error("One or more files necessary for the intent_details.xlsx file was not output by Rasa and thus this file cannot be generated.\n")


def misclassified_intents_df(language_path: str, timestamp: str) -> pd.DataFrame:
    with open(join(language_path, "results", timestamp, "intent_errors.json"), "r") as f:
        intent_errors = json.load(f)

    wrong_intents = defaultdict(lambda: defaultdict(list))
    for error in intent_errors:
        wrong_intents[error["intent"]][
            error["intent_prediction"]["name"]
        ].append(error["text"])

    return pd.DataFrame(
        [
            {
                "intent": k,
                "confused_with": value,
                "utterances": "\n".join(v[value]),
            }
            for k, v in wrong_intents.items()
            for value in v
        ]
    )


def stats_table(language_path: str, timestamp: str) -> pd.DataFrame:
    with open(join(language_path, "results", timestamp, "intent_report.json"), "r") as f:
        intent_report = json.load(f)

    stats_list = []
    for key_, value_ in intent_report.items():
        if key_ not in ["accuracy", "micro_avg", "macro_avg", "weighted_avg"]:
            stats_list.append([key_, round(value_["precision"], 3), round(value_["recall"], 3), round(value_["f1-score"], 3)])

    stats_table = pd.DataFrame(
        stats_list, columns=["intent", "precision", "recall", "f1-score"]
    )
    return stats_table.sort_values("precision", ascending=True)


def confusion_table_df(language_path: str, timestamp: str) -> pd.DataFrame:
    with open(join(language_path, "results", timestamp, "intent_report.json"), "r") as f:
        intent_report = json.load(f)

    confusion_list = []
    for key_, value_ in intent_report.items():
        if key_ not in ["accuracy", "micro avg", "macro avg", "weighted avg"]:
            for intent, count in value_["confused_with"].items():
                confusion_list.append([key_, intent, count])
    confusion_table = pd.DataFrame(
        confusion_list, columns=["intent", "confused_with", "count"]
    )
    return confusion_table.sort_values("count", ascending=False)


def get_all_languages(path: str, languages: tuple) -> list:
    if len(languages) == 0:
        _inform_language()
        languages_paths = [
            join(path, "languages", folder)
            for folder in os.listdir(join(path, "languages"))
            if os.path.isdir(os.path.join(path, "languages", folder))
        ]
    else:
        languages_paths = [
            join(path, "languages", folder)
            for folder in os.listdir(join(path, "languages"))
            if os.path.isdir(os.path.join(path, "languages", folder)) and folder in languages
        ]
    return languages_paths


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the test command.
    """
    print_info(
        "No language was provided but a multi-language bot was detected. "
        "Will test all available languages inside provided bot folder.\n"
    )


if __name__ == "__main__":
    command()
