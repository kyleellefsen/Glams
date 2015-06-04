# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 20:23:47 2013

@author: kyle
"""

#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.txt') as file:
    long_description = file.read()
    
setup(name='Glams',
      version='0.2.5',
      description='A browser based animal management system',
      license='MIT',
      long_description=long_description,
      author='Kyle Ellefsen',
      author_email='kyleellefsen@gmail.com',
      url='https://github.com/kyleellefsen/Glams/',
      packages=find_packages(),
      install_requires=['cherrypy >= 3.2.2',
                        'mysql-connector-python >= 1.2.2',
                        'lxml >= 3.2.0' ],
      include_package_data=True,
     )