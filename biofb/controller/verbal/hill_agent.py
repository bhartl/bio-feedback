from biofb.controller.audio import KeyAgent
from numpy import ndarray
import os.path


class HillAgent(KeyAgent):

    def __init__(self,
                 keymap: (str, dict) = "data/controller/hill/hill_agent_keymap.yml",
                 name: str = "Hill Agent",
                 description: str = "Prerecorded Hill wav spoken samples.",
                 **kwargs
                 ):
        """

        :param keymap: Dict-like or path to dict-like object, specifying the `keymap_action` and `action_map`
                       required by the `KeyAgent` and by the `KeySession`.
        :param name:
        :param description:
        :param kwargs:
        """

        keymap_action, action_map, kwargs = self.__init_keymap(keymap, kwargs)

        KeyAgent.__init__(self,
                          name=name,
                          description=description,
                          keymap_action=keymap_action,
                          action_map=action_map,
                          **kwargs
                          )

    def __init_keymap(self, keymap, kwargs) -> tuple:

        keymap = self.load_dict_like(keymap)

        if 'keymap_action' not in kwargs or 'action_map' not in kwargs:
            assert 'wavfile_keymap' in keymap
            wavfile_keymap = keymap.pop('wavfile_keymap')

            if 'keymap_action' not in kwargs:
                keymap_action = {line['key']: line['label'] for line in wavfile_keymap}
            else:
                keymap_action = kwargs.pop('keymap_action')

            if 'action_map' not in kwargs:
                action_map = {line['label']: line['file'] for line in wavfile_keymap}
            else:
                action_map = kwargs.pop('action_map')
        else:
            keymap_action = kwargs.pop('keymap_action')
            action_map = kwargs.pop('action_map')

        # check if every key label has an action map pendant
        for key, label in keymap_action.items():
            assert label in action_map.keys(), f"Key {key}'s label `{label}` not specified in predefined action_map."

        # check if each audio is either a numpy array or is an existing wav-file path
        for label, audio in action_map.items():
            if isinstance(audio, str):
                abs_path = os.path.abspath(audio)  # for crossplatform
                assert os.path.isfile(abs_path), f"Audio file `{abs_path}` for label `{label}` does not exist"
            else:
                assert isinstance(audio, ndarray)

        kwargs = dict(**kwargs, **keymap)  # merge possible kwargs with remaining keymap dict
        return keymap_action, action_map, kwargs
