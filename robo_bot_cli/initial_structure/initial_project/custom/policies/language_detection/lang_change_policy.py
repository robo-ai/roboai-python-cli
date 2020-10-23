import os
import json
import logging
import typing
from typing import Any, List, Text, Optional

from fasttext import load_model
import numpy as np

import rasa.utils.io

from rasa.core.domain import Domain #, InvalidDomain
from rasa.core.policies import Policy
from rasa.core.actions.action import ACTION_LISTEN_NAME

from rasa.core.featurizers import TrackerFeaturizer
from rasa.core.trackers import DialogueStateTracker
from rasa.core.constants import FALLBACK_POLICY_PRIORITY
from rasa.core.events import UserUttered
from rasa.utils.common import raise_warning

logger = logging.getLogger(__name__)

class LangChangePolicy(Policy):

    def __init__(
        self,
       # featurizer: Optional[TrackerFeaturizer],
        priority: int = FALLBACK_POLICY_PRIORITY,
        model = None,
        lang_detect_threshold: float = 0.8,
        fallback_action_name: Text = "action_ask_language",
        model_path: Text = './language_detection/lid.176.ftz'
    ) -> None:
        """ Create a Language Detection Fallback Policy:
    
        Args:
            lang_detect_threshold: lower threshold for which to assume 
                language detection prediction reliable above that value.
                If both latest predictions execed this threshold, then 
                incoherence among lastest predictions should trigger 
                fallback action
            fallback_action_name: name of the action to execute as a fallback
        """

        super().__init__(priority=priority)

        self.lang_detect_threshold = lang_detect_threshold
        self.fallback_action_name = fallback_action_name
        self.model_path = model_path
        # print(self.model_path)
        self.model = model or self._default_model(self.model_path)

        # attributes that need to be restored after loading
        self._pickle_params = ["model"]
        
        logger.debug(f"Adopted LCP threshold: {self.lang_detect_threshold}")
        logger.debug(f"LCP action to fall out: {self.fallback_action_name}")
    
    @staticmethod
    def _default_model(path) -> Any:
        # print(path)
        return load_model(path)

    @property
    def _state(self):
        return {attr: getattr(self, attr) for attr in self._pickle_params}
        
    def train(
        self,
        training_trackers: List[DialogueStateTracker],
        domain: Domain,
        **kwargs: Any,
    ) -> None:
        """Loads a pretrained language id fasttext model"""
        self.model = load_model(self.model_path)
        print("modelo carregado")
        
    def predict_action_probabilities(self, tracker, domain):

        def predict_language(skip=0):
            fetcher = tracker.get_last_event_for(UserUttered, skip=skip)
            if fetcher is not None:
                user_utter = fetcher.as_dict().get("text")
                language_prediction = self.model.predict(user_utter)
                # print(language_prediction)
                return language_prediction

        def Q_lang_detect_above_threshold(prediction):
            if prediction and prediction is not None:
                return (float(prediction[1]) > self.lang_detect_threshold) 
                    
        latest_lang_prediction = predict_language()
        if predict_language(skip=1):
            previous_lang_prediction = predict_language(skip=1)
        elif tracker.get_slot("language_slot"):
            language_code = tracker.get_slot("language_slot")
            previous_lang_prediction = (((f'__label__{language_code}'),), np.array([1.0]))# to have the same type as fasttext model output
        else:
            previous_lang_prediction = None
        
        logger.debug(f"language present prediction is: {latest_lang_prediction}")
        logger.debug(f"previous language prediction is: {previous_lang_prediction}")
        
        result = self._default_predictions(domain)

        if (
            tracker.latest_action_name == self.fallback_action_name
            and tracker.latest_action_name != ACTION_LISTEN_NAME
        ):
            logger.debug(
                "Predicted 'action_listen' after fallback action '{}'".format(
                    self.fallback_action_name
                )
            )
            result = self._default_predictions(domain)
            idx = domain.index_for_action(ACTION_LISTEN_NAME)
            result[idx] = 1.0

        elif (
            previous_lang_prediction is not None and
            all([Q_lang_detect_above_threshold(x) for x in [latest_lang_prediction, previous_lang_prediction]]) and
            previous_lang_prediction[0][0] != latest_lang_prediction[0][0]
            ):
            idx = domain.index_for_action(self.fallback_action_name)
            if idx is None:
                raise_warning(
                    f"LangChangePolicy tried to predict unknown "
                    "action \"{self.fallback_action_name}\". Make sure to map this actions"
                    "in the domain and run it the custom action server.",
                )
            else:
                result[idx] = 1
        
        return result

    def persist(self, path: Text) -> None:
        """
        Persistes meta data and model once 
        """
    # if self.model:

        meta_file = os.path.join(path, "langchangepolicy.json")
        meta = {"priority": self.priority,
                "lang_detect_threshold": self.lang_detect_threshold,
                "fallback_action_name": self.fallback_action_name,
                "model_path": self.model_path,
            }
        rasa.utils.io.create_directory_for_file(meta_file)
        rasa.utils.io.dump_obj_as_json_to_file(meta_file, meta)

        # model_file = os.path.join(path, "fastext_model.pkl")
        # rasa.utils.io.pickle_dump(model_file, self._state)
        # else:
        #     raise_warning(
        #         "Persist called without a model present. "
        #         "Nothing to persist then!"
        #     )

    @classmethod
    def load(cls, path: Text) -> "LangChangePolicy":
        """Returns the class with the configured priority."""
        
        
        # if not os.path.exists(path):
        #     raise OSError(
        #         "Failed to load dialogue model. Path {} "
        #         "doesn't exist".format(os.path.abspath(path))
        #     )

        meta = {}
#        state = {}
        if os.path.exists(path):
            meta_path = os.path.join(path, "langchangepolicy.json")
            # model_file = os.path.join(path, "fastext_model.pkl")
            if os.path.isfile(meta_path):
                meta = json.loads(rasa.utils.io.read_file(meta_path))
            # if os.path.isfile(model_file):
            #     state = rasa.utils.io.pickle_load(model_file)
            #     logger.info("Loaded language detection model")

        # policy = cls(**meta)

        # vars(policy).update(state)

        return cls(**meta)