"%PREFIX%\Scripts\jupyter-nbextension" disable nb_anacondacloud --py --sys-prefix && "%PREFIX%\Scripts\jupyter-serverextension" disable nb_anacondacloud --py --sys-prefix && if errorlevel 1 exit 1
