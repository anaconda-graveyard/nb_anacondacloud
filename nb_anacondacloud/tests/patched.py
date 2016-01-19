import json
import os

try:
    from unittest.mock import patch
except ImportError:
    # py2
    from mock import patch

import nb_anacondacloud.nbextension as nbac

join = os.path.join

AM = "nb_anacondacloud.nbextension.uploader.AccountManager"
BCMO = "binstar_client.mixins.organizations.OrgMixin"

FIXTURES = join(os.path.dirname(__file__), "fixtures")


def fixture(*bits):
    with open(os.path.join(FIXTURES, *bits)) as fp:
        return json.load(fp)


def load_jupyter_server_extension(nb_app):
    """Load the nb anaconda client extension"""

    nb_app.log.info("Patching nb_anacondacloud")

    # Always allow access
    is_logged_in = patch("{}.is_logged_in".format(AM), autospec=True)
    is_logged_in.return_value = True
    is_logged_in.start()

    # Always give acme
    user_orgs = patch("{}.user_orgs".format(BCMO), autospec=True)
    user_orgs.return_value = fixture("user_orgs.json")
    user_orgs.start()

    nbac.load_jupyter_server_extension(nb_app)
