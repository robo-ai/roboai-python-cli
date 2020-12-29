
All notable changes to this project will be documented in this file.

## [0.1.4] - 2020-12-29

Bugfixes:
* [#14](https://github.com/robo-ai/roboai-python-cli/issues/14): Remove engine validations since it was coming as None from the core.

Features:
* [#20](https://github.com/robo-ai/roboai-python-cli/issues/20): Add cross-validation option to test command.
* Test results are now stored in a generated folder with the timestamp in which the tests were run.
* Intent details spreadsheet now contains a separate tab with intent statistics (precision, recall and f1-score).

## [0.1.3.1] - 2020-11-25

Bugfixes:
* [#11](https://github.com/robo-ai/roboai-python-cli/issues/11): There was a bug in the diff command whenever there were intents which trigger actions defined in the domain.
* [#12](https://github.com/robo-ai/roboai-python-cli/issues/12): There was a bug in the test command whenever there were intents which trigger actions defined in the domain. The same applies also to the stories command.

Features:
* Added a Rasa component (ExactMatchClassifier) which tries to match an intent existent in the NLU. A development pipeline was also added to the initial structure where this component is used instead of a Machine Learning model.
* As a consequence of the topic above, the train command also suffered modifications. Now you can pass a specific config file to be ran (i.e. --dev-config config-dev-.yml). If this option is not passed, the default config.yml will be used.

## [0.1.2] - 2020-11-03

Bugfixes: 
* [#6](https://github.com/robo-ai/roboai-python-cli/issues/8): Test output now also contains the misclassified utterances for easier fixing.
* [#7](https://github.com/robo-ai/roboai-python-cli/issues/7): Comments in the stories file was generating some messy results in the conversation tests file - it should be fixed now.
* [#8](https://github.com/robo-ai/roboai-python-cli/issues/6): .botignore file was being overwritten - now it's only being generated if it doesn't exist.

## [0.1.1] - 2020-10-22

* Added tutorials for creating and deploying Rasa chatbots as well as creating a bot and generating API keys on the Robo AI platform.
* [#3](https://github.com/robo-ai/roboai-python-cli/issues/3): Fixed bug in the deployment command. Fixed minor bugs.

## [0.1.0] - 2020-10-14

* Initial version.
