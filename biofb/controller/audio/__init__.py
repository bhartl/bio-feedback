""" Bio-controller controller-controller module for controller recorded data controller (breathing, ambient noise, preprocesses sounds).

Audio signals or music can directly connect with our emotions.
Music can specifically be composed for that purpose.
For instance, [`Weightless` (Marconi Union)](https://www.youtube.com/watch?v=UfcAVejslrU) is specifically `designed` to slow down the heart beat.

Extracting characteristic sounds, such as

- (calming) breathing noises,
- the sound of a heartbeat,
- etc.

can be used by a controller to guide the bio-signal state of a participant towards a desired value. """

from .key_agent import KeyAgent
from .key_session import KeySession
