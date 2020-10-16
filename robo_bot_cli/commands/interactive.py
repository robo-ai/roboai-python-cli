import click
import os
from os.path import join, abspath


@click.command(name='interactive', help='Run in interactive learning mode where you can \
provide feedback to the required bot.')
@click.argument('language', nargs=1,)
def command(language: str):
    """
    Wrapper of rasa interactive for a multi-language bot.

    Args:
        language (str): language code of the bot for rasa interactive to be run
    """
    start_interactive_mode(language)


def start_interactive_mode(language: str):

    model_path = join(abspath('.'), 'languages', language,
                      'models', f'model-{language}.tar.gz')
    config_path = join(abspath('.'), 'languages', language, 'config.yml')
    domain_path = join(abspath('.'), 'languages', language, 'domain.yml')
    nlu_path = join(abspath('.'), 'languages', language, 'data')
    stories_path = join(abspath('.'), 'languages', 'stories.md')
    endpoints_path = join(abspath('.'), 'endpoints.yml')
    out_path = join(abspath('.'), 'languages', language, 'interactive')

    os.system(f'rasa interactive --model {model_path} --config {config_path} --domain {domain_path} \
            --data {stories_path} {nlu_path} --endpoints {endpoints_path} --out {out_path}')


if __name__ == "__main__":
    command()

# rasa shell --model $model --debug --endpoints $endpoints
