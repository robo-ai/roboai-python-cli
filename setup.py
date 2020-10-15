from setuptools import setup
from robo_bot_cli import __version__


setup(
    name='robo-bot',
    version=__version__,
    py_modules=['robo_bot_cli'],
    install_requires=[
        'click',
        'colorama',
        'cursor',
        'halo',
        'polling',
        'pyfiglet',
        'termcolor',
        'robo-ai',
        'rasa',
        'pandas',
        'openpyxl',
        'pytablewriter'
    ],
    entry_points={"console_scripts": ["robo-bot=robo_bot_cli:run"]},
)
