from biofb.controller import HillAgent
from biofb.controller import AudioKeySession as KeySession
from biofb.session import Sample
import yaml as yaml


class DummySample(Sample):
    """ A dummy Sample object required by the KeystrokeSession """
    def __init__(self, *args, **kwargs):
        pass

    @property
    def state(self):
        return None


def main(action_successive=False, path="data/controller/hill/hill_agent_keymap.yml"):
    """ Example of a Hill-Session which can replay recorded spoken phrases via an interactive keymap

    :param action_successive: Boolean controlling (if true) whether played notes can not be interrupted by next command,
                              or the next action replaces the old one (defaults to True).
    :param path: Path or dict-like with hill-agent-keymap information.
    """

    print(f'Replay Hill wav recordings specified via {path}:')
    print(yaml.safe_dump(HillAgent.load_dict_like(path)))
    print()

    try:

        # Generate a KeystrokeAgent which can be used to detect sound actions based on keystrokes (or the absence thereof)
        hill_agent = HillAgent(
            name='Hill Agent',
            description='Select spoken phrases according to keymap.',
            keymap=path,
        )

        session = KeySession(
            name='Bit-Nots Session',
            description='Replay notes according to keymap.',
            sample=DummySample(),
            agent=hill_agent,
            action_successive=action_successive,
        )

        # print info
        print(hill_agent)

        session.run()

    except KeyboardInterrupt:
        print('Stopped')

    finally:
        del hill_agent, session

    print('Done.')
    return 0


if __name__ == '__main__':
    import argh
    argh.dispatch_command(main)
