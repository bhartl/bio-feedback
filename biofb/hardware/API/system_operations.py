import platform
import sys
import os.path

OS_DIC = {"Darwin": "MacOS",
          "Linux": "Linux64",
          "Windows": ("Win32", "Win64")}

API_ROOT = os.path.dirname(__file__)


def get_platform_lib_path(api_path):
    """ get platform dependent lib-path of API-root directory

    :param api_path: API root directory (str).
    :return: str representing the `api_path/{PLATFORM DEPENDENT SUB-FOLDER}`
    """

    if platform.system() != "Windows":
        return os.path.join(api_path, OS_DIC[platform.system()])

    else:
        if platform.architecture()[0] == '64bit':
            return os.path.join(api_path, "Win64")
        else:
            return os.path.join(api_path, "Win32")


def append_sys_path(lib_path, is_abspath=False):
    """ Append a library path (e.g., including API specific *.dll's under Windows or *.so under Linux) to the system path
    :param lib_path: API-specific library path (str).
    :param is_abspath: Boolean specifying whether the `lib_path` is an absolute path,
                       otherwise `lib_path` is assumed to be a sub-folder within the
                       `biofb.hardware.API.API_ROOT` directory.
    :return: results of `sys.path.append(lib_path)`
    """

    if not is_abspath:
        lib_path = os.path.join(API_ROOT, lib_path)

    # if platform.system() == "Windows":
    #     lib_path = lib_path.replace('/', '\\')

    return sys.path.append(lib_path)
