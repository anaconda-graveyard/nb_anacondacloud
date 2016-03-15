import json
import os


try:
    from unittest import mock
except ImportError:
    import mock

from binstar_client import Binstar
from binstar_client.mixins.organizations import OrgMixin

import nb_anacondacloud as nbac

join = os.path.join

FIXTURES = join(os.path.dirname(__file__), "fixtures")


def fixture(*bits):
    with open(os.path.join(FIXTURES, *bits)) as fp:
        return json.load(fp)


def load_jupyter_server_extension(nb_app):
    """Load the nb anaconda client extension"""

    nb_app.log.info("Patching nb_anacondacloud")

    cls_patches = {
        Binstar: ["user", "upload", "package", "release"],
        OrgMixin: ["user_orgs"]
    }

    for cls, patches in cls_patches.items():
        for method in patches:
            mock.patch.object(
                cls,
                method,
                return_value=fixture("{}.json".format(method))
            ).start()

    nbac.load_jupyter_server_extension(nb_app)
