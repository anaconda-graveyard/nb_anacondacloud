import glob
import os
import shutil
import subprocess

try:
    from unittest.mock import patch
except ImportError:
    # py2
    from mock import patch


from notebook import jstest
from binstar_client.utils import dirs

import platform

IS_WIN = "Windows" in platform.system()

here = os.path.dirname(__file__)

# TODO: Needed because of the number of different streams... needs better
# interleaving
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
        super(NBAnacondaCloudTestController,
              self).__init__(section, *args, **kwargs)
        self.xunit = True

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

    def use_token(self):
        return os.environ.get("USE_ANACONDA_TOKEN", None)

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

    # copy pasta from...
    # https://github.com/jupyter/notebook/blob/master/notebook/jstest.py#L234
    def setup(self):
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
        os.makedirs(os.path.join(self.nbdir.name,
                                 os.path.join(u'sub dir1', u'sub dir 1a')))
        os.makedirs(os.path.join(self.nbdir.name,
                                 os.path.join(u'sub dir2', u'sub dir 1b')))

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
                self.cmd = [
                    jstest.sys.executable, '-c', 'raise SystemExit(1)']

    def add_xunit(self):
        """ Hack the setup in the middle (after paths, before server)
        """
        super(NBAnacondaCloudTestController, self).add_xunit()

        with patch.dict(os.environ, self.env.copy()):
            prefix = (["--sys-prefix"] if ("CONDA_ENV_PATH" in os.environ) or
                      ("CONDA_DEFAULT_ENV" in os.environ) else ["--user"])
            pkg = ["--py", "nb_anacondacloud"]
            install_results = [
                subprocess.Popen(["jupyter"] + cmd + prefix + pkg,
                                 stdout=subprocess.PIPE,
                                 env=os.environ
                                 ).communicate()
                for cmd in [
                    ["serverextension", "enable"],
                    ["nbextension", "install"],
                    ["nbextension", "enable"]
                ]]

            if any(sum(install_results, tuple())):
                raise Exception(install_results)

            if (self.section == "auth") and self.use_token():
                home = os.environ["HOME"]
                _data_dir = "".join([
                    self.home.name,
                    dirs.user_data_dir[len(home):]])

                with open(TEST_LOG, "a+") as fp:
                    fp.write("\nCopying auth token to {}\n".format(
                        _data_dir
                    ))

                shutil.copytree(
                    dirs.user_data_dir,
                    _data_dir
                )

            # we patch the auth by changing the configuration... probably
            # a cleaner way to do it...
            patch_auth = False
            if (self.section == "auth") and not self.use_token():
                patch_auth = True
            nbac = "disable" if patch_auth else "enable"
            nbac_p = "enable" if patch_auth else "disable"

            with open(TEST_LOG, "a+") as fp:
                fp.write("\n\n\n-------------\n{} nbac:{} nbac_p:{}".format(
                    self.section,
                    nbac, nbac_p
                ))

            toggles = [
                [nbac, "nb_anacondacloud"],
                [nbac_p, "nb_anacondacloud.tests.patched"]]

            for toggle, ext in toggles:
                subprocess.Popen(
                    ["jupyter", "serverextension", toggle] + prefix + [ext],
                    stdout=subprocess.PIPE,
                    env=os.environ
                ).communicate()

    def cleanup(self):
        if hasattr(self, "stream_capturer"):
            captured = self.stream_capturer.get_buffer().decode(
                'utf-8', 'replace')
            with open(TEST_LOG, "a+") as fp:
                fp.write("-----------------------\n{} results:\n{}\n".format(
                    self.section,
                    self.server_command))
                fp.write(captured)

        super(NBAnacondaCloudTestController, self).cleanup()


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
