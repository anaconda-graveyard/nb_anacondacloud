import os
from notebook.utils import url_path_join
from .nbextension.handlers import PublishHandler, WhoAmIHandler


def _jupyter_server_extension_paths():
    return [dict(module="nb_anacondacloud")]


def _jupyter_nbextension_paths():
    return [
        dict(
            section="notebook",
            src=os.path.join("static"),
            dest="nb_anacondacloud/",
            require="nb_anacondacloud/main.js")
    ]


def load_jupyter_server_extension(nb_app):
    """Load the nb_anacondacloud client extension"""
    webapp = nb_app.web_app
    base_url = webapp.settings['base_url']
    ns = r'anaconda-cloud'
    webapp.add_handlers(".*$", [
        (url_path_join(base_url, ns, r"publish"), PublishHandler),
        (url_path_join(base_url, ns, r"login"), WhoAmIHandler)
    ])
    nb_app.log.info("Enabling nb_anacondcloud")


raise 1
