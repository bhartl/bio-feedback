import numpy as np
from biofb.controller import KeyAgent
from biofb.controller.audio import AudioKeySession as KeySession
import os
from scipy.io import wavfile

# calculate note frequencies based on A1
FREQUENCIES = {
    k: 440 * 2 ** (i / 12)
    for i, k in enumerate(['A1', 'A1#',
                           'B1',
                           'C1', 'C1#',
                           'D1', 'D1#',
                           'E1',
                           'F1', 'F1#',
                           'G1', 'G1#',
                           'A2', 'A2#',
                           ])
}

DATA_PATH = "data.local/controller/audio/key/"


class DummySample(object):
    """ A dummy Sample object required by the KeystrokeSession """
    def __init__(self, *args, **kwargs):
        pass

    @property
    def state(self):
        return None


def main_array(duration: float = 0.5, sample_rate: int = 44100, frequencies=FREQUENCIES, action_successive=True):
    """ Example of a Key-Session which can play musical notes

    Adapted `simpleaudio` from https://simpleaudio.readthedocs.io/en/latest/tutorial.html

    :param duration: Duration in seconds
    :param sample_rate: Sampling rates of the sounds, i.e. data-points per second
    :param frequencies: Dictionary mapping `{note-names: frequencies}` in Hz.
    :param action_successive: Boolean controlling (if true) whether played notes can not be interrupted by next command,
                              or the next action replaces the old one (defaults to True).
    """

    print('Generate audio signals of the following frequencies [Hz]:')
    [print(f'\t{k}:\t{f}') for k, f in frequencies.items()]
    print()

    audios = dict()  # dictionary mapping
    keymap_notes = dict()

    # get time-steps for each sample, T is note duration in seconds
    t = np.linspace(0, float(duration), int(float(duration) * int(sample_rate)), False)

    for i, (key, freq) in enumerate(frequencies.items()):
        # generate sine wave notes
        note = np.sin(freq * t * 2 * np.pi)

        # normalize to 16-bit range: -32768 to 32767
        audio = note * (2 ** 15 - 1) / np.max(np.abs(note)) / (freq / frequencies['A1'])

        # convert to 16-bit data
        audio = audio.astype(np.int16)

        audios[key] = audio
        keymap_notes[chr(ord('a') + i)] = key

    # Generate a KeystrokeAgent which can be used to detect sound actions based on keystrokes (or the absence thereof)
    agent = KeyAgent(
        name='Bit-Notes Agent',
        description='Select notes according to keymap.',
        keymap_action=keymap_notes,
    )

    session = KeySession(
        name='Bit-Nots Session',
        description='Replay notes according to keymap.',
        sample=DummySample(),
        agent=agent,
        action_map=audios,
        action_successive=action_successive,
        # replay kwargs:
        sample_rate=sample_rate,
    )

    # print info
    print(agent)

    try:
        session.run()

    except KeyboardInterrupt:
        print('Stopped')

    finally:
        del agent, session

    print('Done.')
    return 0


def main_wav(duration: float = 0.5, sample_rate: int = 44100, frequencies=FREQUENCIES, action_successive=False,
             path=DATA_PATH):
    """ Example of a Key-Session which can play musical notes

    Adapted `simpleaudio` from https://simpleaudio.readthedocs.io/en/latest/tutorial.html

    :param duration: Duration in seconds
    :param sample_rate: Sampling rates of the sounds, i.e. data-points per second
    :param frequencies: Dictionary mapping `{note-names: frequencies}` in Hz.
    :param action_successive: Boolean controlling (if true) whether played notes can not be interrupted by next command,
                              or the next action replaces the old one (defaults to True).
    :param path: Wave-file path in which wave-files of notes are stored to and loaded from.
    """

    print('Generate audio signals of the following frequencies [Hz]:')
    [print(f'\t{k}:\t{f}') for k, f in frequencies.items()]
    print()

    audios = dict()  # dictionary mapping
    keymap_notes = dict()

    # get time-steps for each sample, T is note duration in seconds
    t = np.linspace(0, float(duration), int(float(duration) * int(sample_rate)), False)

    for i, (key, freq) in enumerate(frequencies.items()):
        # generate sine wave notes
        note = np.sin(freq * t * 2 * np.pi)

        # normalize to 16-bit range: -32768 to 32767
        audio = note * (2 ** 15 - 1) / np.max(np.abs(note)) / (freq / frequencies['A1'])

        # convert to 16-bit data
        audio = audio.astype(np.int16)

        if not os.path.exists(os.path.abspath(path)):
            os.makedirs(os.path.abspath(path))

        filename = os.path.join(path, f'{key}.wav')
        wavfile.write(os.path.abspath(filename), sample_rate, audio)

        audios[key] = filename
        keymap_notes[chr(ord('a') + i)] = key

    # Generate a KeystrokeAgent which can be used to detect sound actions based on keystrokes (or the absence thereof)
    agent = KeyAgent(
        name='Bit-Notes Agent',
        description='Select notes according to keymap.',
        keymap_action=keymap_notes,
    )

    session = KeySession(
        name='Bit-Nots Session',
        description='Replay notes according to keymap.',
        sample=DummySample(),
        agent=agent,
        action_map=audios,
        action_successive=action_successive,
        # replay kwargs:
        sample_rate=sample_rate,
    )

    # print info
    print(agent)

    try:
        session.run()

    except KeyboardInterrupt:
        print('Stopped')

    finally:
        del agent, session

    print('Done.')
    return 0


if __name__ == '__main__':
    import argh
    argh.dispatch_commands([main_array, main_wav])
