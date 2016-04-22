# flake8: noqa
from ._version import *
from .handlers import load_jupyter_server_extension


def _jupyter_server_extension_paths():
    return [dict(module="nb_anacondacloud")]


def _jupyter_nbextension_paths():
    return [
        dict(
            section="notebook",
            src="static",
            dest="nb_anacondacloud",
            require="nb_anacondacloud/main")
    ]
