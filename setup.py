# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


version = '0.1-dev'

here = os.path.abspath(os.path.dirname(__file__))


def read_file(*pathes):
    path = os.path.join(here, *pathes)
    if os.path.isfile(path):
        with open(path, 'r') as desc_file:
            return desc_file.read()
    else:
        return ''

desc_files = (('README.rst',), ('docs', 'CHANGES.rst'),
              ('docs', 'CONTRIBUTORS.rst'))

long_description = '\n\n'.join([read_file(*pathes) for pathes in desc_files])

install_requires = ['setuptools', 'mr.bobby']


setup(name='bobbyplugins.jpcw',
      version=version,
      description="Flexible rendering plugins for mrbobby",
      long_description=long_description,
      platforms=["any"],
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: Implementation"
                   " :: CPython",
                   "Programming Language :: Python :: Implementation :: PyPy",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "License :: OSI Approved :: BSD License"],
      keywords='mrbobby plugin template',
      author='Jean-Philippe Camguilhem',
      author_email='jpcw__at__camguilhem.net',
      url='https://github.com/jpcw/bobbyplugins.jpcw',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['bobbyplugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={
          'test': [
              'nose',
              'coverage<3.6dev',
              'flake8<2.0',
              'mock',
          ],
          'development': [
              'zest.releaser',
              'Sphinx',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [mr.bobby.plugins]
      render_filename=bobbyplugins.jpcw.rendering:If_Statement
      """,
      )

# vim:set et sts=4 ts=4 tw=80:
