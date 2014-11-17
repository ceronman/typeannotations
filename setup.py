# -*- coding: utf-8 -*-
from __future__ import with_statement

from distutils.core import setup


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except (IOError, OSError):
        return


setup(
    name='typeannotations',
    version='0.1.0',
    description='A library with a set of tools for annotating types '
                'in Python code.',
    long_description=readme(),
    url='https://github.com/ceronman/typeannotations',
    author='Manuel Cerón',
    author_email='ceronman' '@' 'gmail.com',
    license='Apache License',
    packages=['annotation'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
