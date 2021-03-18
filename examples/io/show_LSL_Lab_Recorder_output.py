import pyxdf
import matplotlib.pyplot as plt
import numpy as np
import yaml


def main(xdf_path='data/session/sample/lsl/sub-P001/ses-S002/eeg/sub-P001_ses-S002_task-Default_run-001_eeg.xdf'):
    """ show data captured with the LSL Lab Recorder (xdf format)

        :param xdf_path: Path to the LSL Lab Recorder output file

        If possible, channel meta-data are shown.
    """
    data, header = pyxdf.load_xdf(xdf_path)

    for stream in data:
        y = stream['time_series']

        if isinstance(y, list):
            # list of strings, draw one vertical line for each marker
            for timestamp, marker in zip(stream['time_stamps'], y):
                plt.axvline(x=timestamp)
                print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
        elif isinstance(y, np.ndarray):
            # numeric data, draw as lines

            print(yaml.dump(dict(stream['info'])))

            try:
                labels = []
                for d in stream['info']['desc']:
                    for c in d['channels']:
                        for ch in c['channel']:
                            label = ch['label'][0]
                            unit = ch['unit'][0] if ch['unit'][0] is not None else "-"
                            labels += [f"{label} [{unit}]"]
            except TypeError:
                labels = None

            plt.plot(stream['time_stamps'], y, label=labels)

            if labels is not None:
                plt.legend()

        else:
            raise RuntimeError('Unknown stream format')

    plt.show()


if __name__ == '__main__':
    import argh
    argh.dispatch_command(main)
