from setuptools import find_packages, setup
setup(
    name='libofbabel',
    packages=find_packages(include=['libofbabel']),
    version='0.0.1',
    description='Library Of Babel Python wrapper',
    author='m1raynee',
    license='MIT',
    install_requires=[],
    setup_requires=['requests'],
)