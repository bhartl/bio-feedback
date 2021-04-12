""" bio-feedback pipelines package for synchronized data handling """

STREAM_TYPES = ('name', 'type', 'hostname')

from .receiver import Receiver
from .transmitter import Transmitter

try:
    from .lab_streaming_layer_receiver import LSLReceiver
    from .lab_streaming_layer_transmitter import LSLTransmitter

except RuntimeError:
    LSLReceiver = Receiver  # TODO: clean up
    LSLTransmitter = Transmitter  # TODO: clean up
