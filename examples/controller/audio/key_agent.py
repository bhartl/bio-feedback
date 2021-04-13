import numpy as np
import simpleaudio as sa
from biofb.controller import KeyAgent

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


def main(duration: float = 0.5, sample_rate: int = 44100, frequencies=FREQUENCIES, continuous_playing=False):
    """ Example of a Key-Agent which can play musical notes

    Adapted `simpleaudio` from https://simpleaudio.readthedocs.io/en/latest/tutorial.html

    :param duration: Duration in seconds
    :param sample_rate: Sampling rates of the sounds, i.e. data-points per second
    :param frequencies: Dictionary mapping `{note-names: frequencies}` in Hz.
    :param continuous_playing: Boolean controlling (if true) whether played notes can be interupted by next command,
                               defaults to False.
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
        name='Bit-Notes Player',
        description='Play notes according to keymap.',
        keymap_action=keymap_notes,
    )

    # print info
    print(agent)

    try:
        # loop until `ESC` is pressed
        action = agent.action(state=None)
        while action is not None:
            if action != ():  # check whether a `not None` or `not 0` action was taken

                __, audio = action
                play_obj = sa.play_buffer(audios[audio], 1, 2, sample_rate)

                if not continuous_playing:
                    play_obj.wait_done()

            action = agent.action(state=None)

    except KeyboardInterrupt:
        print('Stopped')

    finally:
        del agent

    print('Done.')
    return 0


if __name__ == '__main__':
    import argh
    argh.dispatch_command(main)
