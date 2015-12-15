import setuptools

setuptools.setup(
    name="nb_anaconda_cloud",
    version='0.1.0',
    url="http://github.com/anaconda-notebook/anaconda-notebook",
    author="Continuum Analytics",
    description="Integration with Anaconda-Cloud",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires=['anaconda-client']
)
