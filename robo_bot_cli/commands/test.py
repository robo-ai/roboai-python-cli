import click
import os
from os.path import abspath, join, exists, isfile, basename, dirname
from os import listdir, mkdir
import json
from pytablewriter import MarkdownTableWriter
import pandas as pd
import random
from re import sub, search

from robo_bot_cli.util.cli import print_info, print_error
from robo_bot_cli.util.input_output import load_md, load_yaml


@click.command(name='test', help='Test Rasa models for the required bots.')
@click.argument('languages', nargs=-1,)
def command(languages: tuple):
    """Tests a Rasa bot.

    Args:
        languages (tuple): languages (bots) to be tested. If no language is passed
                           it checks if the current bot is a multi-language bot. If so
                           all bots will be tested. Otherwise the single-language bot will
                           be tested.
    """
    if len(languages) == 0:
        if exists(join(abspath('.'), 'languages')):
            # multi-language bot
            bot_dir = get_all_languages(path=abspath('.'), languages=languages)
            multi_language_bot = True
        else:
            # single-language bot
            bot_dir = [abspath('.')]
            multi_language_bot = False
    else:
        multi_language_bot = True
        bot_dir = get_all_languages(path=abspath('.'), languages=languages)
    test(bot_dir, multi_language_bot)


def test(languages_path: list, multi_language_bot: bool) -> None:
    for language in languages_path:
        lang = basename(language) if basename(language) != 'bot' else 'the'
        print_info(f"Starting tests for {lang} bot")
        # Check if tests folder exists
        if exists(join(language, 'tests')):
            # Check if tests folder contains any file
            if any(isfile(join(language, 'tests', i)) for i in listdir(join(language, 'tests'))):
                # Check if intents are already covered in the existing test files
                # If there are intents left to be tested, the user is prompted
                # with an option to continue testing
                if check_covered_intents(language):
                    test_bot(language)
                else:
                    exit(0)
            # If tests folder is empty, generate a test stories file
            else:
                generate_conversation_md_from_stories(language, multi_language_bot)
                test_bot(language)
        # If tests folder doesn't exist, create it and generate a test stories file
        else:
            generate_conversation_md_from_stories(language, multi_language_bot)
            test_bot(language)
        format_results(language)
        print_info(f"Finished testing {lang} bot")


def test_bot(language: str):
    os.system(f"rasa test --model {join(language, 'models')} --nlu {join(language, 'data')} \
              --stories {join(language, 'tests')} --out {join(language, 'results')}")


def check_covered_intents(language_path: str) -> bool:
    intents = load_yaml(join(language_path, 'domain.yml')).get('intents', None)
    if intents is None:
        print_error("No intents were found.\n")
        exit(0)
    else:
        for filename in listdir(join(language_path, 'tests')):
            if filename.endswith('.md'):
                lines = load_md(join(language_path, 'tests', filename))
                for line in lines:
                    for intent in intents:
                        if intent in line:
                            intents.remove(intent)
                            break
        if intents:
            print("The following intents are not covered in your test stories:")
            print(*intents, sep="\n")
            should_test = click.confirm("Continue testing?\n")
        else:
            should_test = True
        return should_test


def get_intent_example(intent: str, nlu) -> str:
    examples = []
    copy = False
    comment = False
    for line in nlu:
        if line.startswith("##") and search(r'\b'+intent+r'\b', line):
            if comment is False:
                copy = True
        elif line.startswith('##') and not search(r'\b'+intent+r'\b', line):
            if comment is False:
                copy = False
        elif line.startswith('<!--'):
            comment = True
        elif line.endswith('-->\n'):
            comment = False
        elif copy:
            # examples.append(line.replace('-', '', 1).strip())
            examples.append(sub(r'\{[^)]*\}', '', line).replace('[', '').replace(']', '').replace('-', '', 1).strip())
    examples = [i for i in examples if i]
    if examples:
        return random.choice(examples)
    else:
        return ''


def generate_conversation_md_from_stories(path_to_language: str, multi_language_bot: bool):
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
        stories_path = join(path_to_language, 'data')

    all_stories = []
    for filename in listdir(stories_path):
        if isfile(join(stories_path, filename)):
            if 'stories' in filename:
                stories = load_md(join(stories_path, filename))
                all_stories.append(stories)
    all_stories = [item for sublist in all_stories for item in sublist]
    all_nlu = []
    for filename in listdir(join(path_to_language, 'data')):
        if isfile(join(path_to_language, 'data', filename)):
            if 'stories' not in filename:
                nlu = load_md(join(path_to_language, 'data', filename))
                all_nlu.append(nlu)
    all_nlu = [item for sublist in all_nlu for item in sublist]
    output_path = join(path_to_language, 'tests', 'conversation_tests.md')
    if not exists(join(path_to_language, 'tests')):
        mkdir(join(path_to_language, 'tests'))
    with open(output_path, 'w', encoding='utf-8') as out_f:
        for line in stories:
            if line.startswith('*'):
                intent = sub(r'\{[^)]*\}', '', line).replace('[', '').replace(']', '').replace('*', '', 1).strip()
                if ' or ' in line.lower():
                    first_intent = intent.split()[0]
                    out_f.write(f'* {first_intent}: {get_intent_example(first_intent, all_nlu)}\n')
                else:
                    intent = sub(r'\{[^)]*\}', '', line).replace('[', '').replace(']', '').replace('*', '', 1).strip()
                    out_f.write(f'* {intent}: {get_intent_example(intent, all_nlu)}\n')
            else:
                out_f.write(line)


def generate_conversation_md(path_to_language: str):
    """Generates test stories based on the intents available in the domain.
    Complex stories are not generated.

    Args:
        path_to_language (str): path to language folder.
        If it's a single-language bot this will be the bot root's folder.
    """
    domain = load_yaml(join(path_to_language, 'domain.yml'))
    intents_list = domain.get('intents', None)
    all_nlu = []
    for filename in listdir(join(path_to_language, 'data')):
        if isfile(join(path_to_language, 'data', filename)):
            if 'stories' not in filename:
                nlu = load_md(join(path_to_language, 'data', filename))
                all_nlu.append(nlu)

    all_nlu = [item for sublist in all_nlu for item in sublist]
    if not intents_list:
        print_error("No intents were found.")
        exit(0)
    elif intents_list:
        output_path = join(path_to_language, 'tests', 'conversation_tests.md')
        if not exists(join(path_to_language, 'tests')):
            mkdir(join(path_to_language, 'tests'))
        with open(output_path, 'w', encoding='utf-8') as out_f:
            for intent in intents_list:
                out_f.write(f'## {intent}\n')
                out_f.write(f'* {intent}: {get_intent_example(intent, all_nlu)}\n')
                out_f.write(f'  - utter_{intent}\n')
                out_f.write('\n')


def format_results(language_path: str):
    intents = intent_table(language_path)
    confusion_list = confusion_table(language_path)
    with open(join(language_path, 'results', 'intents_details.md'), 'w') as f:
        f.write(intents)
        f.write("\n\n\n")
        f.write(confusion_list)


def confusion_table(language_path: str) -> None:
    writer = MarkdownTableWriter()
    writer.table_name = "Confusion table"

    with open(join(language_path, 'results', 'intent_report.json')) as f:
        intent_report = json.load(f)

    confusion_list = []
    for key_, value_ in intent_report.items():
        if key_ not in ['accuracy', 'micro avg', 'macro avg', 'weighted avg']:
            for intent, count in value_['confused_with'].items():
                confusion_list.append([key_, intent, count])
    confusion_table = pd.DataFrame(confusion_list, columns=['intent', 'confused_with', 'count'])
    confusion_table = confusion_table.sort_values('count', ascending=False)

    writer.headers = confusion_table.columns.tolist()

    writer.value_matrix = [
        [row['intent']] + [row['confused_with']] + [row['count']]
        for index, row in confusion_table.iterrows()
    ]
    return writer.dumps()


def intent_table(language_path: str):
    writer = MarkdownTableWriter()
    writer.table_name = "Intents"

    with open(join(language_path, 'results', 'intent_report.json'), 'r') as f:
        data = json.loads(f.read())

    cols = ["support", "f1-score", "confused_with"]
    writer.headers = ["class"] + cols

    classes = [key_ for key_ in data.keys() if key_ not in ['accuracy', 'micro avg', 'macro avg', 'weighted avg']]
    classes.sort(key=lambda x: data[x]['support'], reverse=True)

    def format_cell(data, c, k):
        if not data[c].get(k):
            return "N/A"
        if k == "confused_with":
            return ", ".join([f"{k}({v})" for k, v in data[c][k].items()])
        else:
            return data[c][k]

    writer.value_matrix = [
        [c] + [format_cell(data, c, k) for k in cols]
        for c in classes
    ]

    return writer.dumps()


def get_all_languages(path: str, languages: tuple) -> list:
    if len(languages) == 0:
        _inform_language()
        languages_paths = [join(path, 'languages', folder) for folder in os.listdir(join(path, 'languages'))
                           if os.path.isdir(os.path.join(path, 'languages', folder))]
    else:
        languages_paths = [join(path, 'languages', folder) for folder in os.listdir(join(path, 'languages'))
                           if os.path.isdir(os.path.join(path, 'languages', folder)) and folder in languages]
    return languages_paths


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the test command.
    """
    print_info("No language was provided but a multi-language bot was detected. "
               "Will test all available languages inside provided bot folder.\n")


if __name__ == "__main__":
    command()
