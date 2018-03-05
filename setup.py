from setuptools import setup, find_packages

__version__ = 'v0.2'
REQUIRED_PACKAGES = ['colorama']
IGNORE_PACKAGES = ['examples']
FOUND_PACKAGES = find_packages(exclude=IGNORE_PACKAGES)
KEEP_PACKAGES = [i_pack for i_pack in FOUND_PACKAGES if i_pack not in IGNORE_PACKAGES]

setup(
    name='build_with_docker',
    version=__version__,
    description='Python script that runs your python repos within a specified Dockerfile.',
    url='https://github.com/Dammi87/build-with-docker/archive/%s.tar.gz' % __version__,
    install_requires=REQUIRED_PACKAGES,
    packages=KEEP_PACKAGES,
    include_package_data=True,
    requires=[],
    license='MIT',
    keywords=['Docker', 'build'],
    author='Adam Runarsson',
    author_email='adam.runars@gmail.com',
    entry_points={
        'console_scripts': [
            'bwd = bwd.__init__:main'
        ]},

)