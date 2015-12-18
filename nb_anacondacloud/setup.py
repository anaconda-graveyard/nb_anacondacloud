from nbsetuptools import setup, find_static


setup(
    name="nb_anacondacloud",
    version="0.1.0",
    static=join(abspath(dirname(__file__)), 'static')
)
