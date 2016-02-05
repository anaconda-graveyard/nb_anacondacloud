import setuptools

setuptools.setup(
    name="nb_anacondacloud",
    version='0.1.2',
    url="https://github.com/Anaconda-Server/nb_anacondacloud",
    author="Continuum Analytics",
    description="Integration with Anaconda-Cloud",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['anaconda-client']
)
