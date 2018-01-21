import os

import sys
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='gpg-copy',
    version='0.1',
    py_modules=['gpgcopy'],
    entry_points={
        'console_scripts': [
            'gpg-copy=gpgcopy:copy_files',
        ],
    },
    include_package_data=True,
    license='MIT',
    description='Tool for recursive encryption of files with GPG',
    url='https://github.com/ViktorStiskala/gpg-copy',
    author='Viktor Stískala',
    author_email='viktor@stiskala.cz',
    install_requires=['Click'],
    classifiers=[
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
)
