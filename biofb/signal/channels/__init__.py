""" Function collection for channel analysis

[1] The different biosignalsplux sensors are listed on their `website <https://biosignalsplux.com/products/sensors.html>`_
[2] The official `website for the g.tec Unicorn <https://www.unicorn-bi.com/>`_ 8-channel EEG cap (the python interface for this hardware requires a licence key)
"""

from . import accelerometer as acc
from . import audio as audio
from . import blood_volume_pressure as bvp
from . import electro_cardiogram as ecg
from . import electro_dermal_activity as eda
from . import electro_myogram as emg
from . import electro_oculogram as eog
from . import footswitch as fsw
from . import gyroscope as gyr
from . import respiration as pzt
from . import temperature as temp
from . import video as video
