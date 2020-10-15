import pathlib

from setuptools import setup, find_packages
from robo_bot_cli import __version__

SETUP_DIR = pathlib.Path(__file__).parent

README = (SETUP_DIR / "README.md").read_text()

setup(
    name='robo-bot',
    version=__version__,
    description='A command line tool to create, manage and deploy Rasa chatbots.',
    long_description=README,
    long_description_content_type="text/markdown",
    author='ROBO.AI',
    author_email='info@robo-ai.com',
    url='https://github.com/robo-ai/roboai-python-cli',
    license='MIT',
    py_modules=['robo_bot_cli'],
    packages=find_packages(),
    package_data={'': ['initial_structure']},
    setup_requires=['setuptools_scm'],
    include_package_data=True,
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
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["robo-bot=robo_bot_cli:run"]},
)
