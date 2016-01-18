import json
import logging

from tornado import web
from tornado.escape import json_decode

from notebook.utils import url_path_join
from notebook.base.handlers import APIHandler

from binstar_client import errors

from .uploader import Uploader, AccountManager

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class WhoAmIHandler(APIHandler):
    _am = None

    @web.authenticated
    def get(self, **args):
        if self.am.is_logged_in():
            self.finish(json.dumps({
                'user': self.am.user,
                'organizations': self.am.organizations
            }))
        else:
            self.set_status(401)

    @web.authenticated
    def post(self, **args):
        json_body = json_decode(self.request.body)
        try:
            self.am.login(json_body['username'], json_body['password'])
        except errors.Unauthorized:
            self.set_status(401)
        except errors.BinstarError as e:
            self.set_status(400, e)

    @property
    def am(self):
        if self._am is None:
            self._am = AccountManager()
        return self._am


class PublishHandler(APIHandler):
    @web.authenticated
    def post(self, **args):
        json_body = json_decode(self.request.body)
        uploader = Uploader(
            json_body['name'],
            json_body['content'],
            user=json_body.get('organization', None),
            public=json_body.get('public', True),
            env_name=json_body.get('envName', None)
        )
        try:
            self.finish(json.dumps(uploader.upload()))
        except errors.Unauthorized:
            self.set_status(401, "You must login first.")
        except errors.BinstarError as e:
            self.log.error(e)
            self.set_status(400, str(e))


def load_jupyter_server_extension(nb_app):
    """Load the nb anaconda client extension"""
    webapp = nb_app.web_app
    base_url = webapp.settings['base_url']
    webapp.add_handlers(".*$", [
        (url_path_join(base_url, r"/ac-publish"), PublishHandler),
        (url_path_join(base_url, r"/ac-login"), WhoAmIHandler)
    ])
    nb_app.log.info("Enabling nb_anacondanotebook")
