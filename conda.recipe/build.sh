"${PYTHON}" setup.py install
"${PREFIX}/bin/jupyter" nbextension install --sys-prefix --py nb_anacondacloud
