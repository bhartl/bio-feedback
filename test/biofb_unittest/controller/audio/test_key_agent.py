import unittest
from unittest.mock import patch
from os.path import abspath
from pynput.keyboard import Key


class TestKeystrokeAgent(unittest.TestCase):

    def setUp(self) -> None:
        import numpy as np
        import os
        from scipy.io import wavfile

        # calculate note frequencies
        self.frequencies = {
            k: 440 * 2 ** (i/12)
            for i, k in enumerate(['A', 'Ash',
                                   'B',
                                   'C', 'Csh',
                                   'D', 'Dsh',
                                   'E',
                                   'F', 'Fsh',
                                   'G', 'Gsh',
                                   ])
        }

        self.audios = dict()
        self.keymap_files = dict()
        self.keymap_audio = dict()
        self.keymap_freqs = dict()
        self.file_path = "data.local/controller/audio/notes/"

        # get timesteps for each sample, T is note duration in seconds
        self.sample_rate = 44100
        self.T = 0.5
        self.t = np.linspace(0, self.T, int(self.T * self.sample_rate), False)

        for i, (key, freq) in enumerate(self.frequencies.items()):
            # generate sine wave notes
            note = np.sin(freq * self.t * 2 * np.pi)

            # normalize to 16-bit range: -32768 to 32767
            audio = note * (2**15 - 1) / np.max(np.abs(note)) / (freq/self.frequencies['A'])

            # convert to 16-bit data
            audio = audio.astype(np.int16)

            if not os.path.exists(abspath(self.file_path)):
                os.makedirs(abspath(self.file_path))

            filename = f'{self.file_path}{key}.wav'
            wavfile.write(abspath(filename), self.sample_rate, audio)

            self.audios[key] = audio
            self.keymap_files[chr(ord('a') + i)] = filename
            self.keymap_audio[chr(ord('a') + i)] = audio
            self.keymap_freqs[chr(ord('a') + i)] = key

    @patch('biofb.controller.key_agent.KeyAgent.get_pressed_key', return_value=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 0, Key.esc])
    def test_control_notes(self, *args, loud=False, **kwargs):
        from biofb.controller import KeyAgent
        import numpy as np
        import simpleaudio as sa

        k_agent = KeyAgent(
            keymap_action=self.keymap_audio,
            sleep=0. if not loud else 1e-2,
            verbose=False,
        )

        keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        i, imax = 0, 1000
        action = k_agent.action(None)
        while action is not None:

            if action != ():
                __, audio = action
                key = keys.pop(0)

                self.assertTrue(np.array_equal(audio, self.keymap_audio[key]))

                if loud:
                    play_obj = sa.play_buffer(audio, 1, 2, self.sample_rate)

                    # wait for playback to finish before exiting
                    play_obj.wait_done()

            if i >= imax:
                k_agent._terminated = True

            i += 1
            action = k_agent.action(None)

        k_agent.terminate()
        del k_agent


if __name__ == '__main__':
    unittest.main()
