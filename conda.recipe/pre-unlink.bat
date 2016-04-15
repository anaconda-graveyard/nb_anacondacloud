"%PREFIX%\Scripts\jupyter" nbextension disable --sys-prefix --py nb_anacondacloud && "%PREFIX%\Scripts\jupyter" serverextension disable --sys-prefix --py nb_anacondacloud && if errorlevel 1 exit 1
