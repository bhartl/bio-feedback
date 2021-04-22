import unittest


class TestSimpleaudio(unittest.TestCase):

    def test_simpleaudio(self, loud=False):
        """ simpleaudio test-code from https://realpython.com/playing-and-recording-sound-python/

        included `loud` flag for annoyance avoidance during unit-testing.

        Under *Linux* the Python-package `simpleaudio` requires the following library to be installed:
        ```sudo apt-get install libasound2-dev```

        :param loud: Boolean controlling whether sound is played on the speakers (defaults to False)
        """

        import simpleaudio as sa
        import numpy as np

        frequency = 440  # Our played note will be 440 Hz
        fs = 44100  # 44100 samples per second
        seconds = 1  # Note duration of 1 seconds

        # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
        t = np.linspace(0, seconds, seconds * fs, False)

        # Generate a 440 Hz sine wave
        note = np.sin(frequency * t * 2. * np.pi)

        # Ensure that highest value_dict is in 16-bit range
        audio = note * (2**15 - 1) / np.max(np.abs(note))
        # Convert to 16-bit data
        audio = audio.astype(np.int16)

        if loud:
            # Start playback
            play_obj = sa.play_buffer(audio, 1, 2, fs)

            # Wait for playback to finish before exiting
            play_obj.wait_done()

    def test_simpleaudio_stereo(self, loud=False):
        """ simpleaudio test-code from https://realpython.com/playing-and-recording-sound-python/

        included `loud` flag for annoyance avoidance during unit-testing.

        Under *Linux* the Python-package `simpleaudio` requires the following library to be installed:
        ```sudo apt-get install libasound2-dev```

        :param loud: Boolean controlling whether sound is played on the speakers (defaults to False)
        """

        import numpy as np
        import simpleaudio as sa

        # calculate note frequencies
        A_freq = 440
        Csh_freq = A_freq * 2 ** (4 / 12)
        E_freq = A_freq * 2 ** (7 / 12)

        # get timesteps for each sample, T is note duration in seconds
        sample_rate = 44100
        T = 1.5
        t = np.linspace(0, T, int(T * sample_rate), False)

        # generate sine wave notes
        A_note = np.sin(A_freq * t * 2 * np.pi)
        Csh_note = np.sin(Csh_freq * t * 2 * np.pi)
        E_note = np.sin(E_freq * t * 2 * np.pi)

        # mix audio together
        audio = np.zeros((len(t), 2))
        n = int(len(t)//2)

        offset = 0
        audio[0 + offset: n + offset, 0] += A_note[0 + offset: n + offset]
        audio[0 + offset: n + offset, 1] += 0.125 * A_note[0 + offset: n + offset]
        offset = 5500

        audio[0 + offset: n + offset, 0] += 0.5 * Csh_note[0 + offset: n + offset]
        audio[0 + offset: n + offset, 1] += 0.5 * Csh_note[0 + offset: n + offset]
        offset = 11000

        audio[0 + offset: n + offset, 0] += 0.125 * E_note[0 + offset: n + offset]
        audio[0 + offset: n + offset, 1] += E_note[0 + offset: n + offset]

        # normalize to 16-bit range
        audio *= 32767 / np.max(np.abs(audio))
        # convert to 16-bit data
        audio = audio.astype(np.int16)

        if loud:
            # start playback
            play_obj = sa.play_buffer(audio, 2, 2, sample_rate)

            # wait for playback to finish before exiting
            play_obj.wait_done()


if __name__ == '__main__':
    unittest.main()
