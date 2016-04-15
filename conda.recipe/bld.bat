"%PYTHON%" setup.py install && "%PREFIX%\Scripts\jupyter" nbextension install --overwrite --sys-prefix --py nb_anacondacloud && if errorlevel 1 exit 1
