import platform
import re
import StringIO
import time
from binstar_client import errors
from binstar_client.utils import get_binstar, store_token
from binstar_client.utils.notebook.inflection import parameterize


class Uploader(object):
    _package = None
    _release = None
    _project = None

    def __init__(self, name, content, public=True, user=None):
        self.aserver_api = get_binstar()
        self.name = parameterize(name)
        self.content = content
        self.version = time.strftime('%Y.%m.%d.%H%M')
        self.summary = "IPython notebook"
        self.public = public
        self.username = user
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
            return self.aserver_api.upload(self.username, self.project, self.version,
                                           self.name, self.content_io(),
                                           re.sub('\-ipynb$', '', self.name))
        except errors.Conflict:
            if force:
                self.remove()
                return self.upload()
            else:
                msg = "Conflict: {} already exist in {}/{}".format(self.filepath,
                                                                   self.project,
                                                                   self.version)
                raise errors.BinstarError(msg)

    def content_io(self):
        _notebook = StringIO.StringIO()
        _notebook.write(self.content)
        _notebook.seek(0)
        return _notebook

    def remove(self):
        return self.aserver_api.remove_dist(self, self.username, self.project,
                                            self.version, basename=self.notebook)

    @property
    def project(self):
        if self._project is None:
            return re.sub('\-ipynb$', '', self.name)
        else:
            return self._project

    @property
    def package(self):
        if self._package is None:
            try:
                self._package = self.aserver_api.package(self.username, self.project)
            except errors.NotFound:
                self._package = self.aserver_api.add_package(self.username, self.project,
                                                             summary=self.summary,
                                                             attrs={})
        return self._package

    @property
    def release(self):
        if self._release is None:
            try:
                self._release = self.aserver_api.release(self.username, self.project, self.version)
            except errors.NotFound:
                self._release = self.aserver_api.add_release(self.username, self.project,
                                                             self.version, None, None, None)
        return self._release


class AccountManager(object):
    def __init__(self):
        self._user = None
        self.aserver_api = get_binstar()

    def is_logged_in(self):
        return self.user is not None

    def login(self, username, password):
        token = self.get_token(username, password)
        fake_args = FakeArgs(username, password)
        store_token(token, fake_args)

    def get_token(self):
        return self.aserver_api.authenticate(
            self.username, self.password, 'https://api.anaconda.org',
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
            output.append(
                {'name': org['name'], 'login': org['login']}
            )
        return output


class FakeArgs(object):
    def __init__(self, username, password):
        self.token = None
        self.site = None
        self.hostname = None
        self.login_username = username
        self.login_password = password
