import glob
import json
import os
import shutil
import subprocess
import sys

try:
    from unittest.mock import patch
except ImportError:
    # py2
    from mock import patch

import requests

from notebook import jstest
from ipython_genutils.tempdir import TemporaryDirectory
from binstar_client.utils import dirs

import platform

IS_WIN = "Windows" in platform.system()

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
        super(NBAnacondaCloudTestController,
              self).__init__(section, *args, **kwargs)

        test_cases = glob.glob(os.path.join(
            here, 'js', section, 'test_*.js'))
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

        if IS_WIN:
            self.cmd[0] = "{}.cmd".format(self.cmd[0])

    def launch(self, buffer_output=False, capture_output=False):
        # print('*** ENV:', self.env)  # dbg
        # print('*** CMD:', self.cmd)  # dbg
        env = os.environ.copy()
        env.update(self.env)
        if buffer_output:
            capture_output = True
        self.stdout_capturer = c = jstest.StreamCapturer(
            echo=not buffer_output)
        c.start()
        stdout = c.writefd if capture_output else None
        # stderr = subprocess.STDOUT if capture_output else None
        self.process = subprocess.Popen(
            self.cmd,
            stderr=subprocess.PIPE,
            stdout=stdout,
            env=env)

    def wait(self):
        self.process.communicate()
        self.stdout_capturer.halt()
        self.stdout = self.stdout_capturer.get_buffer()
        return self.process.returncode

    def _init_server(self):
        nbac_ext = None

        conda = ("CONDA_ENV_PATH" in os.environ or
                 "DEFAULT_ENV_PATH" in os.environ)

        with patch.dict(os.environ, self.env):
            install_results = [
                subprocess.Popen(["jupyter"] + cmd + [
                                       "--sys-prefix" if conda else "--user",
                                       "--py", "nb_anacondacloud"
                                 ]).communicate()
                for cmd in [
                    ["serverextension", "enable"],
                    ["nbextension", "install"],
                    ["nbextension", "enable"]
                ]]
            if any(sum(install_results, tuple())):
                raise Exception(install_results)

        # Run "Real" local integration testing?
        if self.section == "auth":
            if os.environ.get("USE_ANACONDA_TOKEN", None):
                home = os.environ["HOME"]
                _data_dir = "".join([
                    self.home.name,
                    dirs.user_data_dir[len(home):]])

                shutil.copytree(
                    dirs.user_data_dir,
                    _data_dir
                )
            else:
                nbac_ext = "nb_anacondacloud.tests.patched"

        if nbac_ext is None:
            nbac_ext = "nb_anacondacloud.nbextension"

        # THIS IS FROM jstest
        "Start the notebook server in a separate process"
        self.server_command = command = [
            sys.executable,
            '-m', 'notebook',
            '--debug',
            '--no-browser',
            '--notebook-dir', self.nbdir.name,
            '--NotebookApp.base_url=%s' % self.base_url,
            '--NotebookApp.server_extensions=%s' % json.dumps([nbac_ext])
        ]
        # ipc doesn't work on Windows, and darwin has crazy-long temp paths,
        # which run afoul of ipc's maximum path length.
        if sys.platform.startswith('linux'):
            command.append('--KernelManager.transport=ipc')
        self.stream_capturer = c = jstest.StreamCapturer()
        c.start()
        env = os.environ.copy()
        env.update(self.env)
        if self.engine == 'phantomjs':
            env['IPYTHON_ALLOW_DRAFT_WEBSOCKETS_FOR_PHANTOMJS'] = '1'
        self.server = subprocess.Popen(
            command,
            stdout=c.writefd,
            stderr=subprocess.STDOUT,
            cwd=self.nbdir.name,
            env=env,
        )
        with patch.dict('os.environ', {'HOME': self.home.name}):
            runtime_dir = jstest.jupyter_runtime_dir()
        self.server_info_file = os.path.join(
            runtime_dir,
            'nbserver-%i.json' % self.server.pid
        )
        self._wait_for_server()


def prepare_controllers(options):
    """Monkeypatched prepare_controllers for running widget js tests

    instead of notebook js tests
    """
    return (
        [
            NBAnacondaCloudTestController('auth'),
            NBAnacondaCloudTestController('noauth'),
        ],
        []
    )


def test_notebook():
    with patch.object(jstest, 'prepare_controllers', prepare_controllers):
        jstest.main()


if __name__ == '__main__':
    test_notebook()
