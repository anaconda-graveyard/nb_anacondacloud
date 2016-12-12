import json
import logging
import platform
import re
from io import BytesIO
from subprocess import check_output, CalledProcessError
import time
import os

import yaml

from binstar_client import errors
from binstar_client.utils import get_server_api, store_token
from binstar_client.utils.notebook.inflection import parameterize

log = logging.getLogger(__name__)


class Uploader(object):
    _package = None
    _release = None
    _project = None

    def __init__(self, name, content):
        self.aserver_api = get_server_api()
        self.name = parameterize(name)
        self.content = content
        self.summary = self.metadata.get("summary", "Jupyter Notebook")
        self.username = self.metadata.get("organization", None)
        if self.metadata.get("attach-environment", None):
            self.env_name = self.metadata.get("environment", None)
            if self.env_name is None:
                ksname = self.ksname
                if ksname in ["python2", "python3"]:
                    # we are dealing with the native kernel, so let's find out
                    # the name of the env where that kernel lives
                    self.env_name = self.default_env()
                else:
                    # ksname comes in the form conda-env-name-[py/r] or
                    # conda-root-[py/r] so split them and catch the name
                    self.env_name = ksname.split("-")[-2]
        else:
            self.env_name = None

        if self.username is None:
            self.username = self.aserver_api.user()['login']

    def upload(self, force=False):
        """
        Uploads a notebook
        :param force: True/False
        :returns {}
        """
        self.package and self.release
        try:
            return self.aserver_api.upload(
                self.username,
                self.project,
                self.version,
                self.name,
                self.content_io(),
                "ipynb")
        except errors.Conflict:
            if force:
                self.remove()
                return self.upload()
            else:
                msg = "Conflict: {}/{} already exist".format(
                    self.project, self.version)
                raise errors.BinstarError(msg)

    def default_env(self):
        conda_info = self._exec(['conda', 'info', '--json'])

        if not conda_info:
            return None

        conda_info = json.loads(conda_info.decode("utf-8"))

        if conda_info["default_prefix"] == conda_info["root_prefix"]:
            return "root"

        return os.path.basename(conda_info["default_prefix"])

    def attach_env(self, content):
        """ given an environment name, update the content with a normalized
            `conda env import`-compatible environment
        """
        env = yaml.load(
            self._exec(['conda', 'env', 'export',
                        '-n', self.env_name,
                        '--no-builds'])
        )
        # this is almost certainly not useful to anybody else
        env.pop('prefix')

        # this is currently a mess
        channels = env.get("channels", [])
        dependencies = []
        pip_deps = []

        # currently seeing weird stuff
        for dep in env.get("dependencies", []):
            if isinstance(dep, dict):
                if "pip" in dep:
                    pip_deps = dep["pip"]
            else:
                channel = None
                if "::" in dep:
                    channel, dep = dep.split("::")
                if channel is not None:
                    channels.append(channel)
                dependencies.append(dep)

        # i guess no dependencies could happen
        env["dependencies"] = sorted(set(dependencies or []))

        # getting lots of extra pip deps... this might not always be needed
        if pip_deps:
            unique_pip_deps = []
            conda_deps = [cdep.split("=")[0].replace("_", "-")
                          for cdep in dependencies]
            for dep in pip_deps:
                # local files are not reproducible
                if "(" in dep:
                    continue
                pip_dep = dep.split("=")[0]
                if pip_dep.replace("_", "-") not in conda_deps:
                    unique_pip_deps.append(pip_dep)
            if unique_pip_deps:
                env["dependencies"].append({"pip": sorted(unique_pip_deps)})

        # only add channels if you got some
        if channels:
            env["channels"] = channels

        # avoid foot-shooting here
        if env.get("name") == "root":
            env["name"] = "notebook-{}".format(self.name)

        # whew, we made it! it would be great to have a verify step
        content['metadata']['environment'] = env

        return content

    def _exec(self, cmd):
        try:
            output = check_output(cmd)
        except CalledProcessError as e:
            log.error(e)
            output = {}
        return output

    def content_io(self):
        _notebook = BytesIO()

        if self.env_name is not None:
            self.content = self.attach_env(self.content)

        _notebook.write(json.dumps(self.content).encode())
        _notebook.seek(0)
        return _notebook

    def remove(self):
        return self.aserver_api.remove_dist(self, self.username, self.project,
                                            self.version,
                                            basename=self.notebook)

    @property
    def version(self):
        return time.strftime('%Y.%m.%d.%H%M')

    @property
    def project(self):
        if self._project is None:
            return re.sub('\-ipynb$', '', self.name)
        else:
            return self._project

    @property
    def ksname(self):
        ks = self.content.get("metadata", {}).get("kernelspec", {})
        return ks.get("name", None)

    @property
    def metadata(self):
        return self.content.get("metadata", {}).get("anaconda-cloud", {})

    @property
    def notebook_attrs(self):
        attrs = {}

        # thumbnails should be coming back with a proper data URI starting with
        # "data:image/png;base64,"... but the uploader/template will add its
        # own later. Just strip it, or fail if it's not properly formatted
        try:
            attrs['thumbnail'] = self.metadata["thumbnail"].split(",")[1]
        except Exception:
            pass

        return attrs

    @property
    def package(self):
        if self._package is None:
            try:
                self._package = self.aserver_api.package(
                    self.username,
                    self.project)
            except errors.NotFound:
                self._package = self.aserver_api.add_package(
                    self.username,
                    self.project,
                    summary=self.summary,
                    attrs=self.notebook_attrs)
        return self._package

    @property
    def release(self):
        if self._release is None:
            try:
                self._release = self.aserver_api.release(
                    self.username,
                    self.project,
                    self.version)
            except errors.NotFound:
                self._release = self.aserver_api.add_release(
                    self.username,
                    self.project,
                    self.version,
                    None,
                    None,
                    None)
        return self._release


class AccountManager(object):
    def __init__(self):
        self._user = None
        self.aserver_api = get_server_api()

    def is_logged_in(self):
        return self.user is not None

    def login(self, username, password):
        fake_args = FakeArgs(username, password)
        token = self.get_token(fake_args)
        store_token(token, fake_args)

    def get_token(self, args):
        return self.aserver_api.authenticate(
            args.login_username,
            args.login_password,
            'https://api.anaconda.org',
            created_with='nb_anacondacloud', fail_if_already_exists=True,
            hostname=platform.node()
        )

    @property
    def user(self):
        if self._user is None:
            try:
                self._user = self.aserver_api.user()
            except errors.Unauthorized:
                self._user = None
        return self._user

    @property
    def organizations(self):
        output = []
        for org in self.aserver_api.user_orgs():
            if 'name' in org:
                output.append({'name': org['name'], 'login': org['login']})
            else:
                output.append({'name': org['login'], 'login': org['login']})
        return output


class FakeArgs(object):
    def __init__(self, username, password):
        self.token = None
        self.site = None
        self.hostname = None
        self.login_username = username
        self.login_password = password
