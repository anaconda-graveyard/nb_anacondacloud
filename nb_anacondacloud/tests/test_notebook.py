import os
import glob
import sys
import shutil
import subprocess

try:
    from unittest.mock import patch
except ImportError:
    # py2
    from mock import patch

from notebook import jstest
from binstar_client.utils import dirs

here = os.path.dirname(__file__)

# global npm installs are bad, add the local node_modules to the path
os.environ["PATH"] = os.pathsep.join([
    os.environ["PATH"],
    os.path.abspath(os.path.join(here, "node_modules", ".bin"))
])


class NBAnacondaCloudTestController(jstest.JSController):
    """ Javascript test subclass that installs widget nbextension in test
        environment
    """
    def __init__(self, section, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', None)
        super(NBAnacondaCloudTestController, self).__init__(
            section,
            *args,
            **kwargs)

        test_cases = glob.glob(os.path.join(here, 'js', 'test_*.js'))
        js_test_dir = jstest.get_js_test_dir()

        includes = [
            os.path.join(js_test_dir, 'util.js')
        ] + glob.glob(os.path.join(here, 'js', '_*.js'))

        self.cmd = [
            'casperjs', 'test',
            '--includes={}'.format(",".join(includes)),
            '--engine={}'.format(self.engine)
        ] + test_cases

        if extra_args is not None:
            self.cmd = self.cmd + extra_args

    def _init_server(self):
        # copy current user token into the temp directory
        home = os.environ["HOME"]
        _data_dir = "".join([self.home.name, dirs.user_data_dir[len(home):]])

        shutil.copytree(
            dirs.user_data_dir,
            _data_dir
        )

        with patch.dict(os.environ, self.env):
            subprocess.check_call([
                sys.executable, "-m", "nb_anacondacloud.setup",
                "install",
                "--enable",
                "--verbose", "DEBUG",
                "--prefix", self.config_dir.name,
            ])

        super(NBAnacondaCloudTestController, self)._init_server()


def prepare_controllers(options):
    """Monkeypatched prepare_controllers for running widget js tests

    instead of notebook js tests
    """
    if options.testgroups:
        groups = options.testgroups
    else:
        groups = ['']
    return [NBAnacondaCloudTestController(g, extra_args=options.extra_args)
            for g in groups], []


def test_notebook():
    with patch.object(jstest, 'prepare_controllers', prepare_controllers):
        jstest.main()


if __name__ == '__main__':
    test_notebook()
