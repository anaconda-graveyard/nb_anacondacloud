"%PREFIX%\Scripts\jupyter" nbextension enable --sys-prefix  --py nb_anacondacloud && "%PREFIX%\Scripts\jupyter" serverextension enable --sys-prefix --py nb_anacondacloud && if errorlevel 1 exit 1
