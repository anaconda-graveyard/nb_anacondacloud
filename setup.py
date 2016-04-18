import setuptools
from os.path import join

# should be loaded below
__version__ = None

with open(join('nb_anacondacloud', '_version.py')) as version:
    exec(version.read())

setuptools.setup(
    name="nb_anacondacloud",
    version=__version__,
    url="https://github.com/Anaconda-Platform/nb_anacondacloud",
    author="Continuum Analytics",
    description="Upload Jupyter notebooks to anaconda.org with a single click",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['anaconda-client']
)
