""" Python API binding from the
    `biosignalsplux/python-samples git-repo
    <https://github.com/biosignalsplux/python-samples/blob/master/OneDeviceAcquisitionExample.py>`_ (modified and adapted).

    *Note: The code comes with the Apache License 2.0.*
"""

from biofb.hardware.API import system_operations

API_PATH = "PLUX-API-Python3"


try:
    lib_path = system_operations.get_platform_lib_path(API_PATH)
    system_operations.append_sys_path(lib_path, is_abspath=False)

    import plux

except Exception as ex:

    import warnings
    warnings.warn('Could not import `plux` Python3 API.')

    plux = None
