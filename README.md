# NB Anaconda Cloud

## Development

```
git clone
conda env create
source activate nb_anacondacloud

python setup.py develop
cd nb_anacondacloud
python setup.py install --enable --prefix $CONDA_ENV_PATH --symlink

jupyter notebook --no-browser
```

 Happy hacking!
