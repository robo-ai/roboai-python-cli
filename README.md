[![License: MIT](https://img.shields.io/badge/License-MIT-pink.svg)](https://opensource.org/licenses/MIT)

# ROBO.AI Bot Runtime manager CLI tool #

<img align="right" width="200" height="200" alt="robo-bot" src="robo-bot.png"></img>
This tool allows anyone to create, train, deploy, monitor and manage a Rasa based bot on the ROBO.AI platform.  
Check our [CHANGELOG](CHANGELOG.md) for the latest changes.

Tutorials: 
* [The ROBO.AI platform - creating bots and API keys for deployment](docs/manage_roboai_account.md)
* [Creating and deploying a Rasa chatbot on the ROBO.AI platform](docs/create_deploy_bot.md)

### How to install ###

#### Requirements ####

* Python 3.6 or 3.7
* Pip and/or anaconda

You can create a virtual environment using conda:
```sh
conda create -n robo-bot python=3.7
conda activate robo-bot
```

#### Install the ROBO.AI tool ####

Assuming you are already in your virtual environment with Python 3.6 or 3.7, you can install the tool with the following command:
```
pip install robo-bot
```

After installing the library you should be able to execute the robo-bot command in your terminal.

#### Usage ####

The command line tool is available through the following terminal command:

```
robo-bot
```

When you execute it in a terminal you should see an output with a list of commands supported
by the tool.

I.e:
```
user@host:~$ robo-bot
 ____   ___  ____   ___           _    ___ 
|  _ \ / _ \| __ ) / _ \         / \  |_ _|
| |_) | | | |  _ \| | | |       / _ \  | | 
|  _ <| |_| | |_) | |_| |  _   / ___ \ | | 
|_| \_\\___/|____/ \___/  (_) /_/   \_\___|
Bot Management Tool             robo-ai.com

Usage: robo-bot [OPTIONS] COMMAND [ARGS]...

  robo-bot 0.1.0

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  clean        Clean the last package
  connect      Connect a local bot to a ROBO.AI server bot instance.
  deploy       Deploy the current bot into the ROBO.AI platform.
  diff         Check for structural differences between languages for the...
  environment  Define the ROBO.AI platform API endpoint to use.
  interactive  Run in interactive learning mode where you can provide...
  login        Initialize a new session using a ROBO.AI API key.
  logout       Close the current session in the ROBO.AI platform.
  logs         Display selected bot runtime logs.
  package      Package the required bot and make it ready for deployment.
  remove       Remove a deployed bot from the ROBO.AI platform.
  run          Start the action server.
  seed         Create a new ROBO.AI project seedling, including folder...
  shell        Start a shell to interact with the required bot.
  start        Start a bot deployed on the ROBO.AI platform.
  status       Display the bot status.
  stories      Generate stories for a Rasa bot.
  stop         Stop a bot running in the ROBO.AI platform.
  test         Tests Rasa models for the required bots.
  train        Trains Rasa models for the required bots.
``` 

Each of the listed commands provides you a functionality to deal with your bots,
each one has a description, and a help option, so you can see what options and
arguments are available.

You can invoke each of the tool commands by following the pattern:
```
robo-bot <command> [command arguments or options]
```

i.e.:
```
robo-bot login --api-key=my-apy-key
```

You can check the supported options and arguments for every command by following
the pattern:

```
robo-bot <command> --help
```

i.e.:

```
user@host:~$ robo-bot login --help
 ____   ___  ____   ___           _    ___ 
|  _ \ / _ \| __ ) / _ \         / \  |_ _|
| |_) | | | |  _ \| | | |       / _ \  | | 
|  _ <| |_| | |_) | |_| |  _   / ___ \ | | 
|_| \_\\___/|____/ \___/  (_) /_/   \_\___|
Bot Management Tool             robo-ai.com

Usage: robo-bot login [OPTIONS]

  Initialize a new session using a ROBO.AI API key.

Options:
  --api-key TEXT  The ROBO.AI platform API key.
  --help          Show this message and exit.
```

### Using robo-bot to create and maintain a bot ###

##### Generating an initial structure #####

The ROBO.AI tool provides you with a set of commands useful to create, train, interact and test a bot 
before its deployment. 

To create a bot you can use the **seed** command:

```
robo-bot seed [language-codes] [--path <path> --language-detection --chit-chat --coref-resolution]
```
i.e.:
```
robo-bot seed en de --path bot/ --language-detection --chit-chat --coref-resolution
```

The first argument of the seed command is the language-codes which indicate the languages the bot will be built upon. 
If no language-codes are passed, only an english sub-directory (en) will be created. 
The optional parameters are referring to features you may want to add to the bot.  
This command behaves like rasa init but it'll generate a dedicated structure where you can have
multi-language bots related with the same domain. Below there's an example of a bot generated with this command. 

```
.
├── actions
│   └── action_parlai_fallback.py
├── custom
│   ├── components
│   │   └── spacy_nlp
│   │       ├── spacy_nlp_neuralcoref.py
│   │       └── spacy_tokenizer_neuralcoref.py
│   └── policies
│       └── language_detection
│           ├── lang_change_policy.py
│           └── lid.176.ftz
├── languages
|   ├── de
|   │   ├── config.yml
|   │   ├── data
|   │   │   ├── lookup_tables
|   │   │   └── nlu.md
|   │   └── domain.yml
|   ├── en
|   │   ├── config.yml
|   │   ├── data
|   │   │   ├── lookup_tables
|   │   │   └── nlu.md
|   │   └── domain.yml
|   └── stories.md
├── credentials.yml
├── endpoints.yml
└── __init__.py
```

##### Generating stories for a bot #####

After defining intents and actions for a bot you need to combine these in stories. This command allows you to generate the most basic interactions in your Rasa bot. 
Note: Manual checks will be needed to implement more complex stories but basic ping-pong dialogues should be covered with this feature. 
Usage: 
```
robo-bot stories [language-codes] [--check-covered-intents]
```

If no language-code is passed, robo-bot will assume you're working in a single-language bot (and thus the default Rasa structure). 
The option --check-covered-intents will go through your stories file and check if the intents you have defined in the domain file are being covered in the dialogues. This command is more useful when you're deep in the development of your bot.


##### Checking for differences in a bot #####

After making all the necessary changes to your bots, you want to make sure that all bots (languages) are coherent between each other (i.e. the same stories.md file will work for the nlu.md and domain.yml files configured for the different languages.) To know whether your bot is achieving this, you can use the **diff** command. 

```
robo-bot diff [language-codes] [--path <path>]
```

It will check for structural differences between the domain.yml and stories.md files for the same multi-language bot. 
If no language codes are passed, then it'll pair all the languages found and check for differences between them.  


##### Training a bot #####

You're now in a position to train the bot. To do so you only need to run the **train** command just as you would do in Rasa. 

```
robo-bot train [language-codes] [--path <path> --nlu --core --augmentation <value>]
```

It will train the bot and store the model in the language sub-directory. If no language codes are passed, 
all bots will be trained. 

##### Interacting with a bot #####

To interact with the bot, you can use the **shell** command. Before running it, you need to execute the **run actions** command. 

```
robo-bot run actions [--debug]
```

After doing so, you can execute the shell command. 

```
robo-bot shell [language-code] [--debug]
```

You need to specify what language (bot) you want to interact with - you can only interact with one bot at the time.

##### Testing a bot #####

Testing a bot is also probably in your pipeline. And this is possible with the **test** command.

```
robo-bot test [language-code]
```

It'll test the bot with the conversation_tests.md file you have stored in your tests folder.  
The results will be stored in the language sub-directory. Besides Rasa's default results, robo-bot also produces 
an excel file with a confusion list of mistmatched intents.

##### Interactive learning #####

If you want to use Rasa's interactive learning mode you can do this by using the interactive command. 

```
robo-bot interactive [language-code]
```

It'll launch an interactive session where you can provide feedback to the bot. At the end don't forget to
adjust the paths to where the new files should be saved. 

By now you're probably ready to deploy your bot...

### Using robo-bot to deploy a bot ###

##### Setting the target endpoint #####

Before doing any operation you must indicate to the tool in what environment you're working in,
for that you have the **environment** command:

The tool provides you with a default production environment in the ROBO.AI platform.
You can activate it by running:

```
robo-bot environment activate production
```

You can also create new environments by executing:


```
robo-bot environment create <environment name> --base-url <base-url> [--username <username> --password <password>]
```

The base-url refers to the environment URL and you can optionally pass a username
and password if your environment requires them.

i.e.:

```
robo-bot environment create development --base-url https://robo-core.my-robo-server.com --username m2m --password GgvJrZSCXger
```

After creating an environment, do not forget to activate it if you want to use it. 
To know which environment is activated you can simply run:

```
robo-bot environment which
```

It's possible to check what environments are available in your configuration file by running: 

```
robo-bot environment list
```

You can also remove environments by executing:

```
robo-bot environment remove <environment name>
```


##### Logging in #####

Once you have the desired environment activated, you need to login into the account you'd like to use by using
an API key.

1. Log-in into your ROBO.AI administration and generate an API key (do not forget to enable it).
2. Execute the login command and enter the API key.

i.e.:
```
robo-bot login --api-key=my-api-key
```

Or if you don't want to enter the api key in your command, you can enter it interactively by only executing:

```
robo-bot login
```

##### Initializing a bot #####

In order to manage a bot runtime, it needs to be initialized so the tool will know what bot this runtime
refers to. If you already have the Rasa bot initialized, just execute the following command:

```
robo-bot connect [language-code] --target-dir <path to rasa bot files>
```

i.e.:

```
robo-bot connect [language-code] --target-dir /path/to/rasa/bot
```

First it'll ask you to pick an existing bot (if it does not exist, you must create it before executing this step).
After doing it, it'll generate a new file called robo-manifest.json which contains meta-information about the deployment
and the target bot.  
**Note:** if no language-code is provided, it's assumed that you're working with the default Rasa structure.

##### Deploying a bot #####

When your bot is ready for deployment, you must train it first and remove any older model, then ensure you're in
the bot root directory, and then just execute:

```
robo-bot deploy [language-code]
```

It'll package your bot files and upload them to the ROBO.AI platform, starting a new deployment. This step may take
some time.  
**Note:** if no language-code is provided, it's assumed that you're working with the default Rasa structure.

##### Checking a bot status #####

If you want to check your bot status, just run the following command from the same directory as of
your robo-manifest.json

```
robo-bot status [language-code]
```

**Note:** if no language-code is provided, it's assumed that you're working with the default Rasa structure.

##### Removing a bot #####

If you need to remove a bot, execute the following command from the bot root directory:

```
robo-bot remove [language-code]
```

**Note:** if no language-code is provided, it's assumed that you're working with the default Rasa structure.

##### Checking a deployed bot logs #####

Sometimes it's useful to have a peak in the logs, for that you need to execute:

```
robo-bot logs [language-code]
```

It'll show you the latest 1000 lines from that rasa bot logs.  
**Note:** if no language-code is provided, it's assumed that you're working with the default Rasa structure.
