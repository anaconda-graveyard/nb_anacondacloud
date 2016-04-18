"${PYTHON}" setup.py install
"${PREFIX}/bin/jupyter-nbextension" install nb_anacondacloud --py --sys-prefix --overwrite
