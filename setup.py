#!/usr/bin/env python
from setuptools import setup
from setuptools import find_packages

def get_install_required():
    with open("./requirements.txt", "r") as reqs:
        requirements = reqs.readlines()
    return [r.rstrip() for r in requirements]

setup(name='arboretum',
      version='0.1',
      description='Dockable widget for Napari for visualizing cell track data.',
      author='Alan R. Lowe',
      author_email='a.lowe@ucl.ac.uk',
      url='https://github.com/quantumjot/arboretum',
      packages=find_packages(),
      install_requires=get_install_required(),
      python_requires='>=3.6'
     )
