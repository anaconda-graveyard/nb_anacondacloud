import os
import glob
import json
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

    def cleanup(self):
        captured = self.stream_capturer.get_buffer().decode('utf-8', 'replace')
        with open(".jupyter-jstest.log", "w") as fp:
            fp.write(captured)
        super(NBAnacondaCloudTestController, self).cleanup()

    def _init_server(self):
        # TODO:
        # NOT TODO: copy current user token into the temp directory
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
                "--prefix", self.config_dir.name,
            ])

        "Start the notebook server in a separate process"
        self.server_command = command = [
            sys.executable,
            '-m', 'notebook',
            # '--debug',
            '--no-browser',
            '--notebook-dir', self.nbdir.name,
            '--NotebookApp.base_url=%s' % self.base_url,
            '--NotebookApp.server_extensions=%s' % json.dumps([
                'nb_anacondacloud.tests.patched'])
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
