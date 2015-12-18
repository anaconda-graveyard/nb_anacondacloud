import json
import logging

from binstar_client import errors
from tornado import web
from notebook.utils import url_path_join
from notebook.base.handlers import APIHandler
from uploader import Uploader, AccountManager

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ACLoginHandler(APIHandler):
    def __init__(self):
        self.am = AccountManager()

    @web.authenticated
    def get(self, **args):
        if self.am.is_logged_in():
            self.finish()
        else:
            self.set_status(401)

    @web.authenticated
    def post(self, **args):
        json_body = json.loads(self.request.body)
        try:
            self.am.login(json_body['username'], json_body['password'])
        except errors.Unauthorized:
            self.set_status(401)
        except errors.BinstarError as e:
            self.set_status(400, e)


class PublishHandler(APIHandler):
    @web.authenticated
    def post(self, **args):
        json_body = json.loads(self.request.body)
        uploader = Uploader(
            json_body['name'],
            json_body['content'],
            user=json_body.get('user', None),
            public=json_body.get('public', True)
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
        (url_path_join(base_url, r"/ac-login"), ACLoginHandler)
    ])
    nb_app.log.info("Enabling nb_anacondanotebook")
