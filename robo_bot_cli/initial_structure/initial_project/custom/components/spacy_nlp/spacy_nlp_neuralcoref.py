from rasa.nlu.utils.spacy_utils import SpacyNLP

import logging
import typing
from typing import Any, Dict, List, Optional, Text, Tuple

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig, override_defaults
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.model import InvalidModelError
from rasa.core.slots import TextSlot
from datetime import datetime

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from spacy.language import Language
    from spacy.tokens.doc import Doc  # pytype: disable=import-error
    from rasa.nlu.model import Metadata
from spacy.tokens.doc import Doc
from rasa.nlu.constants import TEXT, SPACY_DOCS, DENSE_FEATURIZABLE_ATTRIBUTES
from os.path import exists, join
import os

from rasa.core.trackers import DialogueStateTracker
import spacy

class SpacyNLPNeuralCoref(SpacyNLP):

    defaults = {
        # name of the language model to load - if it is not set
        # we will be looking for a language model that is named
        # after the language of the model, e.g. `en`
        "model": None,
        # when retrieving word vectors, this will decide if the casing
        # of the word is relevant. E.g. `hello` and `Hello` will
        # retrieve the same vector, if set to `False`. For some
        # applications and models it makes sense to differentiate
        # between these two words, therefore setting this to `True`.
        "case_sensitive": False,
    }

    def __init__(self,
                component_config: Dict[Text, Any] = None,
                nlp: "Language" = None,
                max_history: int = 2) -> None:
        print("init Spacy")
        self.session_token = str(datetime.now().strftime("%Y%m%d_%H%M%S.%f"))
        self.max_history = max_history
        self.history = []
        super().__init__(component_config, nlp)

    @staticmethod
    def load_model(spacy_model_name: Text) -> "Language":
        """Try loading the model, catching the OSError if missing."""
        import spacy

        try:
            return spacy.load(spacy_model_name)
        except OSError:
            raise InvalidModelError(
                "Model '{}' is not a linked spaCy model.  "
                "Please download and/or link a spaCy model, "
                "e.g. by running:\npython -m spacy download "
                "en_core_web_md\npython -m spacy link "
                "en_core_web_md en".format(spacy_model_name)
            )

    def doc_for_text(self, text: Text) -> "Doc":
        # text = "why should i wear a mask? where can i buy it?"
        # nlp = spacy.load("en_neuralcoref")
        # print(nlp==self.nlp)
        # doc = nlp(text)
        if not self.history: 
            # if history list is empty (ie contains no previous user messages)
            # generate doc with current message
            # this doc is generated to have access to doc._.coref_resolved
            preprocessed_text = self.preprocess_text(text)
            doc = self.nlp(preprocessed_text)
            result = doc._.coref_resolved
            # we can now add this doc._.coref_resolved to the history list
            self.history.append(result)
        elif self.history: 
            # if history list contains previous user messages 
            # we retrieve the last self.max_history sentences and join them 
            # with the current one 
            # this way, it's possible for the algo to match any pronoun in the current msg
            # with previous saved nouns. 
            lines = self.history[-self.max_history:]
            previous_sentences = (' ').join(lines)
            to_evaluate = previous_sentences + " " + text
            preprocessed_text = self.preprocess_text(to_evaluate)
            doc = self.nlp(preprocessed_text)
            # we want to keep the current message only with the pronoun replaced with the noun 
            result = doc._.coref_resolved[-((len(doc._.coref_resolved)-len(previous_sentences))-1):]
            self.history.append(result)
        # now we generate a new doc based on the result we obtained with doc._.coref_resolved
        new_doc = self.nlp(self.preprocess_text(result))
        # print(result)
        # print(self.nlp(self.preprocess_text(text))._.coref_resolved)
        return new_doc
