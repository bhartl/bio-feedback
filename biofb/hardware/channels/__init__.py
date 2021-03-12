""" Specified hardware channels """

from .accelerometer import ACC
from .blood_volume_pressure import BVP
from .counter import CNT
from .electro_cardiogram import ECG
from .electro_dermal_activity import EDA
from .electro_encephalogram import EEG
from .electro_myogram import EMG
from .footswitch import FSW
from .gyroscope import GYR
from .respiration import PZT
from .temperature import TEMP
from .quality import QC
from .battery import BAT

CHANNEL_MAPPING = {
    'RESPIRATION': PZT,
    'RESP': PZT,
    'CUSTOM*': FSW,
    'ACC*': ACC,
    'EEG*': EEG,
}
""" Hash-Table to map channels to special channel labels. """
