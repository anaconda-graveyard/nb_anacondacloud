import os
import glob
import json
import sys
import subprocess

try:
    from unittest.mock import patch
except ImportError:
    # py2
    from mock import patch

from notebook import jstest

here = os.path.dirname(__file__)

TEST_LOG = ".jupyter-jstest.log"


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

    def cleanup(self):
        captured = self.stream_capturer.get_buffer().decode('utf-8', 'replace')
        with open(TEST_LOG, "a+") as fp:
            fp.write("{} results:\n".format(self.section))
            fp.write(captured)
        super(NBAnacondaCloudTestController, self).cleanup()

    def _init_server(self):
        # always install the extension into the test environment
        with patch.dict(os.environ, self.env):
            subprocess.check_call([
                sys.executable, "-m", "nb_anacondacloud.setup",
                "install",
                "--enable",
                "--prefix", self.config_dir.name,
            ])

        nbac_ext = "nb_anacondacloud"

        if self.section == "auth":
            nbac_ext += ".tests.patched"

        # THIS IS FROM jstest
        "Start the notebook server in a separate process"
        self.server_command = command = [
            sys.executable,
            '-m', 'notebook',
            # '--debug',
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

    def setup(self):
        # the fancy dir names confuse anaconda build
        self.ipydir = jstest.TemporaryDirectory()
        self.config_dir = jstest.TemporaryDirectory()
        self.nbdir = jstest.TemporaryDirectory()
        self.home = jstest.TemporaryDirectory()
        self.env = {
            'HOME': self.home.name,
            'JUPYTER_CONFIG_DIR': self.config_dir.name,
            'IPYTHONDIR': self.ipydir.name,
        }
        self.dirs.append(self.ipydir)
        self.dirs.append(self.home)
        self.dirs.append(self.config_dir)
        self.dirs.append(self.nbdir)
        os.makedirs(os.path.join(
            self.nbdir.name, os.path.join(u'sub dir1', u'sub dir 1a')))
        os.makedirs(os.path.join(
            self.nbdir.name, os.path.join(u'sub dir2', u'sub dir 1b')))

        if self.xunit:
            self.add_xunit()

        # If a url was specified, use that for the testing.
        if self.url:
            try:
                alive = jstest.requests.get(self.url).status_code == 200
            except:
                alive = False

            if alive:
                self.cmd.append("--url=%s" % self.url)
            else:
                raise Exception('Could not reach "%s".' % self.url)
        else:
            # start the ipython notebook, so we get the port number
            self.server_port = 0
            self._init_server()
            if self.server_port:
                self.cmd.append('--url=http://localhost:%i%s' % (
                    self.server_port, self.base_url))
            else:
                # don't launch tests if the server didn't start
                self.cmd = [sys.executable, '-c', 'raise SystemExit(1)']


def prepare_controllers(options):
    """Monkeypatched prepare_controllers for running widget js tests

    instead of notebook js tests
    """
    if os.path.exists(TEST_LOG):
        with open(TEST_LOG, "w") as fp:
            fp.write("Starting test...\n")
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
