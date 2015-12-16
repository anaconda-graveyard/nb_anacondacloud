import json
import logging
import tempfile

from tornado import web
from tornado.escape import json_encode
from notebook.utils import url_path_join
from notebook.base.handlers import APIHandler

from binstar_client import errors
from binstar_client.utils import get_binstar
from binstar_client.utils.notebook.uploader import Uploader

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PublishHandler(APIHandler):
    def initialize(self):
        self.aserver_api = get_binstar()

    def upload(self, name, content):
        with tempfile.NamedTemporaryFile(delete=False) as tfile:
            tfile.write(json.dumps(content))
            tfile.close()

            uploader = Uploader(self.aserver_api, tfile.name)
            uploader.package and uploader.release
            self.aserver_api.upload(
                uploader.username, uploader.project, uploader.version,
                name, open(tfile.name, 'rb'), name.split('.')[-1]
            )

    @web.authenticated
    def post(self, **args):
        if self._is_logged_in():
            try:
                self.upload(
                    json.loads(self.request.body)['name'],
                    json.loads(self.request.body)['content']
                )
                self.write(json_encode({
                    'uploaded': True,
                    'url': 'url'
                }))
            except (errors.BinstarError, IOError):
                self.set_status(500)
        else:
            self.set_status(401)

    def _is_logged_in(self):
        try:
            user = self.aserver_api.user()
            return user
        except errors.Unauthorized:
            return False


def load_jupyter_server_extension(nb_app):
    """Load the nb anaconda client extension"""
    webapp = nb_app.web_app
    base_url = webapp.settings['base_url']
    webapp.add_handlers(".*$", [
        (url_path_join(base_url, r"/ac-publish"), PublishHandler)
    ])
    nb_app.log.info("Enabling nb_anacondanotebook")
