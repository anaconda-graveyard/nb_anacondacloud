"%PYTHON%" setup.py install && "%PREFIX%\Scripts\jupyter-nbextension.exe" install nb_anacondacloud --py --sys-prefix --overwrite && if errorlevel 1 exit 1
