

import typing
from typing import Text, List, Any, Type

from rasa.nlu.tokenizers.spacy_tokenizer import SpacyTokenizer
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.nlu.components import Component
from rasa.nlu.utils.spacy_utils import SpacyNLP
from rasa.nlu.training_data import Message

from rasa.nlu.constants import SPACY_DOCS

if typing.TYPE_CHECKING:
    from spacy.tokens.doc import Doc  # pytype: disable=import-error

POS_TAG_KEY = "pos"

class SpacyTokenizerNeuralCoref(SpacyTokenizer):

    def tokenize(self, message: Message, attribute: Text) -> "Doc":
        doc = self.get_doc(message, attribute)

        return [
            Token(
                t.text, t.idx, lemma=t.lemma_, data={POS_TAG_KEY: self._tag_of_token(t)}
            )
            for t in doc if not t.is_punct
        ] 