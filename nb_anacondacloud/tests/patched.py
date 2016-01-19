import json
import os


try:
    from unittest import mock
except ImportError:
    import mock

from binstar_client import Binstar
from binstar_client.mixins.organizations import OrgMixin

import nb_anacondacloud.nbextension as nbac

join = os.path.join

FIXTURES = join(os.path.dirname(__file__), "fixtures")


def fixture(*bits):
    with open(os.path.join(FIXTURES, *bits)) as fp:
        return json.load(fp)


def load_jupyter_server_extension(nb_app):
    """Load the nb anaconda client extension"""

    nb_app.log.info("Patching nb_anacondacloud")

    # Always allow access
    mock_user = mock.patch.object(
        Binstar, 'user',
        return_value=fixture("user.json"))
    mock_user.start()

    # Always give acme
    mock_org = mock.patch.object(
        OrgMixin, "user_orgs",
        return_value=fixture("user_orgs.json"))
    mock_org.start()

    nbac.load_jupyter_server_extension(nb_app)
