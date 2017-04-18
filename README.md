# NB Anaconda Cloud
[![Install with conda](https://anaconda.org/conda-forge/nb_anacondacloud/badges/installer/conda.svg
)](https://anaconda.org/conda-forge/nb_anacondacloud)
[![Build Status (Lin64)](https://travis-ci.org/Anaconda-Platform/nb_anacondacloud.svg)](https://travis-ci.org/Anaconda-Platform/nb_anacondacloud)
[![Coverage Status](https://coveralls.io/repos/github/Anaconda-Platform/nb_anacondacloud/badge.svg?branch=master)](https://coveralls.io/github/Anaconda-Platform/nb_anacondacloud?branch=master)

## Installation
```shell
conda install -c conda-forge nb_anacondacloud
anaconda login  # optional, but recommended
```
Then, when you launch the Jupyter Notebook, you will see a "cloud upload"
button in the toolbar. Press it, and after ensuring your credentials, you'll
be able to click Publish.

The _Summary_ and _Thumbnail_ fields are currently only populated the first
time you publish!


## Development
```shell
git clone https://github.com/Anaconda-Platform/nb_anacondacloud.git
conda create -y -n nb_anacondacloud python
conda install -y -n nb_anacondacloud -c conda-forge --file requirements.txt
source activate nb_anacondacloud
python setup.py develop
npm install
jupyter nbextension install nb_anacondacloud --py --sys-prefix --symlink
jupyter nbextension enable nb_anacondacloud --py --sys-prefix
jupyter serverextension enable nb_anacondacloud --py --sys-prefix

jupyter notebook --no-browser
```

Happy hacking!

## Tests

### ...the hard way
The tests can either be run with a mocked API (it won't hit the Anaconda Cloud
API)...

```shell
npm run test
```

..or using your anaconda credentials, i.e. from `anaconda login`

```shell
USE_ANACONDA_TOKEN=1 npm run test
```

_NOTE_ This approach will test the package "for reals" by:
  - (potentially) deleting a package called `untitled`
  - publishing a new package `untitled`
  - releasing a notebook in it
  - releasing another notebook to it

## Continuous Integration

Automated tests are run on Travis-CI and Appveyor.


## Changelog

### 1.4.0
- support notebook security fix introduced in notebook 4.3.1

### 1.3.0
- fix bad variable reference in environment name
- fix the attaching of the current environment

### 1.2.0
- update to `nb_conda_kernels` 2.0.0 (and actually depend on it)

### 1.1.0
- fix thumbnail uploading
- CI on Travis and Appveyor
- Coveralls

### 1.0.1
- minor install fixes

### 1.0.0
- update to notebook 4.2
- handle environment uploads better with nb_conda_kernels
