# NB Anaconda Cloud

## Development

```
git clone
conda env create
source activate nb_anacondacloud

# We will remove this 4.2 is released
conda install notebook=5 -c malev -c javascript
python setup.py develop
jupyter nbextension install --py=nb_anacondacloud --overwrite --sys-prefix --symlink
jupyter nbextension enable --py=nb_anacondacloud --sys-prefix
jupyter serverextension enable --py=nb_anacondacloud --sys-prefix

jupyter notebook --no-browser
```

Happy hacking!

## Tests
The tests can either be run with a mocked API (it won't hit the Anaconda Cloud
API)...

```
npm run test
```

Or using your anaconda credentials, i.e. from `anaconda login`

```
USE_ANACONDA_TOKEN=1 npm run test
```

_NOTE_ This approach will test the package "for real" by:
  - (potentially) deleting a package called `untitled`
  - publishing a new package `untitled`
  - releasing a notebook in it
  - releasing another notebook to it
