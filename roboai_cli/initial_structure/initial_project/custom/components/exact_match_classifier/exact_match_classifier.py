import os
import logging
from typing import Any, Dict, Optional, Text

from rasa.nlu import utils
from rasa.nlu.classifiers.classifier import IntentClassifier
from rasa.nlu.constants import INTENT
from rasa.utils.common import raise_warning
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.training_data import TrainingData
from rasa.nlu.model import Metadata
from rasa.nlu.training_data import Message

logger = logging.getLogger(__name__)


class ExactMatchClassifier(IntentClassifier):
    """Intent classifier using simple exact matching.


    The classifier takes a list of keywords and associated intents as an input.
    A input sentence is checked for the keywords and the intent is returned.

    """

    defaults = {"case_sensitive": True}

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        intent_keyword_map: Optional[Dict] = None,
    ):

        super(ExactMatchClassifier, self).__init__(component_config)

        self.case_sensitive = self.component_config.get("case_sensitive")
        self.intent_keyword_map = intent_keyword_map or {}

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:

        for ex in training_data.training_examples:
            self.intent_keyword_map[ex.text] = ex.get(INTENT)

    def process(self, message: Message, **kwargs: Any) -> None:
        intent_name = self._map_keyword_to_intent(message.text)

        confidence = 0.0 if intent_name is None else 1.0
        intent = {"name": intent_name, "confidence": confidence}

        if message.get(INTENT) is None or intent is not None:
            message.set(INTENT, intent, add_to_output=True)

    def _map_keyword_to_intent(self, text: Text) -> Optional[Text]:

        for keyword, intent in self.intent_keyword_map.items():
            if keyword.strip() == text.strip():  # re.search(r"\b" + keyword + r"\b", text, flags=re_flag):
                logger.debug(
                    f"ExactMatchClassifier matched keyword '{keyword}' to"
                    f" intent '{intent}'."
                )
                return intent

        logger.debug("ExactMatchClassifier did not find any keywords in the message.")
        return None

    def persist(self, file_name: Text, model_dir: Text) -> Dict[Text, Any]:
        """Persist this model into the passed directory.

        Return the metadata necessary to load the model again.
        """

        file_name = file_name + ".json"
        keyword_file = os.path.join(model_dir, file_name)
        utils.write_json_to_file(keyword_file, self.intent_keyword_map)

        return {"file": file_name}

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Metadata = None,
        cached_component: Optional["ExactMatchClassifier"] = None,
        **kwargs: Any,
    ) -> "ExactMatchClassifier":

        if model_dir and meta.get("file"):
            file_name = meta.get("file")
            keyword_file = os.path.join(model_dir, file_name)
            if os.path.exists(keyword_file):
                intent_keyword_map = utils.read_json_file(keyword_file)
            else:
                raise_warning(
                    f"Failed to load key word file for `IntentKeywordClassifier`, "
                    f"maybe {keyword_file} does not exist?"
                )
                intent_keyword_map = None
            return cls(meta, intent_keyword_map)
        else:
            raise Exception(
                f"Failed to load keyword intent classifier model. "
                f"Path {os.path.abspath(meta.get('file'))} doesn't exist."
            )
