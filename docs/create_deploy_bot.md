# Creating and deploying a bot with Robo AI's Bot Manager Tool
This tutorial intends to give you an overview of how to create and deploy a simple Rasa chatbot using Robo AI's Bot Manager Command Line Tool. 
For any doubts you might have, please refer to our [README](../README.md) and if you cannot find the answer to your query, you may contact us at info@robo-ai.com.
Prerequisites of this tutorial: <br>
- An account on the Robo AI platform<br>
- A preexisting bot created on the Robo AI platform <br>
- A valid API key<br>
If you have trouble setting up the above please follow this [guide](manage_roboai_account.md).


## Robo AI Bot Manager Command Line Tool  
Robo AI Bot Manager is a CLI tool which allows you to create, manage and deploy Rasa chatbots on the Robo AI platform.


## Installation
To install the tool please make sure you are working on a virtual environment with Python 3.6 or Python 3.7.
You can create a virtual environment using conda:
```sh
conda create -n robo-bot python=3.7
conda activate robo-bot
```

The package can then be installed via pip as follows:
```sh
pip install robo-bot
```

After installing the command line tool, it should be available through the following terminal command: 
```sh
robo-bot
```
When you execute it in a terminal you should see an output with a list of commands supported by the tool.
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

## Usage
As of now, the tool provides you with two major features: <br>
(1) creating and managing Rasa chatbots <br>
(2) deploying Rasa chatbots on the Robo AI platform. <br>
For simplicity purposes we will use the tool to generate a new bot and stories for it. For the remaining of the tutorial we will use our <a href="https://github.com/robo-ai/roboai-demo-faq-chatbot">demo chatbot</a> which you can clone to follow along. 

### Creating a bot
Let's say we want to create a multi-language bot (with English and German being the languages) and a language detection feature where the bot is able to recognize other languages and redirect your users accordingly. This feature is essentially a custom policy which at every user input is classifying the language. Apart from this feature we also included scripts for a custom component and a custom action which you can use as fallback (more on that here). The first step would be to create a folder for our bot's contents. 
```sh
mkdir bot
cd bot
```
We are now ready to generate the initial structure of the bot which is provided to you with this tool. To do so, we only need to run the following command:
```sh
robo-bot seed en de --language-detection
```
The *seed* command will generate the following structure inside the bot directory:
```
.
├── actions
│   ├── action_parlai_fallback.py
│   └── __init__.py
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
|   ├── en
|   │   ├── config.yml
|   │   ├── data
|   │   │   └── nlu.md
|   │   └── domain.yml
|   ├── de
|   │   ├── config.yml
|   │   ├── data
|   │   │   └── nlu.md
|   │   └── domain.yml
|   └── stories.md
├── credentials.yml
├── endpoints.yml
└── __init__.py
```
As you can see we have specific files for the NLU, domain and config files depending on the language but the stories file is common among the two chatbots, meaning you do not have to repeat work and if you do wish to have a small subset of specific dialogues for one of the bots, you can create a stories file and include it in the data folder.

This is the initial step for creating any bot with this tool, the structure is always the one shown above even when you are working with single-language chatbots (i.e. if you pass only one language code to the command).

Imagine now we have developed the NLU and the domain files, with intents and responses. Naturally, the next thing to do will be to generate the stories. With this tool you can generate ping pong dialogues automatically with the *stories* command, assuming your intents and responses for these scenarios have the same name (example: intent "greeting", response "utter_greeting"). If you run 
```sh
robo-bot stories en
```
it will pick up the intents you have defined in the English bot domain file and build the ping pong dialogues in the common stories.md file.
If you are deep in the development of your bot you can also run 
```sh
robo-bot stories en --check-covered-intents
```
and it will check which intents registered in your English domain are not yet covered in the stories file. 

For the remaining of the tutorial we will use our demo chatbot which already contains some content that we can leverage to show how the tool works. This is also a multi-language chatbot written in English and German.
Previously we mentioned that for a lot of cases, the stories file will be common between different languages and this means that we need to check the integrity of our multi-language bot. To do so we can use the *diff* command. The *diff* command will check for differences in intents, actions, entities and responses registered in the different language domains. You can use it in the following way: 
```sh
robo-bot diff en de
```
Alternatively you can also not pass any language code and it will check for differences between all available bots.

Training a bot, launching a shell and running the action server is intended to work exactly as rasa commands. These commands are just wrappers and we only included arguments we thought are the most used among ourselves so if you're missing some argument that you believe should be added please let us know. You can run 
```sh
robo-bot train/shell/run --help
```
to check the available options. 
If we want to train our English bot, we can simply run: 
```sh
robo-bot train en
```
In the background it will call rasa train with the adjusted paths for the necessary files. Note that if you do not pass a language to the command, all bots will be trained. You should also be warned that differently from Rasa we only keep one model at a time. The next time you train your bot, the old model will be overwritten. 

If we want to test our bot locally we can use the shell command as follows:
```sh
robo-bot shell en 
```
It will launch the shell for the English bot. In this case it is mandatory that you pass only one language code. 

Just like in Rasa we also have to launch the action server so that our bot's actions can be executed. In a separate terminal window you can run the following command to run the action server:
```sh
robo-bot run actions
```
Another natural step in the flow is to generate test stories for our bot to see how it is behaving, at least for simple dialogues. The *test* command generates test stories automatically for you based on the bot stories.md file. Using this command does not necessarily mean that you won't have to manually build some test cases but most of the work should be done. If you run 
```sh
robo-bot test en
```
it will check if no test stories already exist and if so it'll automatically create them. After that it will run the rasa test command to run the tests. If there is already a file containing test dialogues then it'll list the intents which are not covered in these dialogues and prompt you to continue with the tests or not.  

Once you're happy with your bot you can deploy it on the Robo AI platform. This part of the tutorial assumes you already have set up an account, you already have enabled an API key and you have already created a bot on the platform. You can check [this tutorial](manage_roboai_account.md) in case you haven't followed those steps. 
This tool already provides you with the environment configuration you need to have for deploying a bot, you just need to activate it. To do so you only need to run
```sh
robo-bot environment activate production
```
This command will create a hidden file in your filesystem with the configuration needed for the following steps. There are other options under the environment command but they are out of scope in this tutorial. 

After activating the environment we can log in on the platform. For that we can use the *login* command in the following way (note that this is a dummy API key): 
```sh
robo-bot login --api-key=9e4r5877-56e5-4211-8d92-c33757bc3f54	
```
You'll take the API key from the platform, in the top right corner > Account > API keys > copy the most suitable one. This command is logging in on the platform, fetching a token and storing it in the configuration file mentioned above. 

Now we need to establish the connection between the bot we have been working on, say the English version, and one that already exists in the platform. To do so we use the connect command as follows: 
```sh
robo-bot connect en --target-dir .
```
It will prompt you with the options available in the platform from which you'll have to select one bot. Based on that selection, the command will generate a file called robo-manifest.json where some metadata will be stored in the path passed in the target-dir argument. This file is needed for the deployment step and thus it should be stored in the root directory of the bot (folder called "bot") because that is what subsequent commands are expecting (hence the target-dir argument pointing to the current directory).

After being done with this step we can finally deploy our bot in the platform by executing: 
```sh
robo-bot deploy en
```
This will generate an image of the bot which will be running on a docker container which you can also check and manage through some available commands. The *logs* command will show you the logs of the bot which should be useful to track some eventual errors.
```sh
robo-bot logs en
```
The *start* command will start a bot that has been deployed on the Robo AI platform. 
```sh
robo-bot start en
```
The *stop* command will stop a bot that is running in the Robo AI platform.
```sh
robo-bot stop en
```
The *remove* command removes a deployed bot from the Robo AI platform. 
```sh
robo-bot remove en
```

These are the fundamental steps to handle this tool. If you have any further questions please don't hesitate to reach out to us. 
