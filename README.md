# NB Anaconda Cloud

## Development

```shell
git clone
conda env create
source activate nb_anacondacloud

python setup.py develop
cd nb_anacondacloud
python setup.py install --enable --prefix $CONDA_ENV_PATH --symlink

jupyter notebook --no-browser
```

Happy hacking!

## Tests

### ...the easy way
```shell
npm run pkg:conda
```

### ...the hard way
Update `npm` and install `casperjs` and other test assets:

```shell
npm install -g npm
npm install
```

The tests can either be run with a mocked API (it won't hit the Anaconda Cloud
API)...

```shell
npm run test
```

..or using your anaconda credentials, i.e. from `anaconda login`

```shell
USE_ANACONDA_TOKEN=1 npm run test
```

## Continuous Integration

Automated tests are run on Anaconda Cloud:

_NOTE_ This approach will test the package "for real" by:
  - (potentially) deleting a package called `untitled`
  - publishing a new package `untitled`
  - releasing a notebook in it
  - releasing another notebook to it


## Changelog

### 1.0.0
- update to notebook 4.2
- handle environment uploads better with nb_conda_kernels
