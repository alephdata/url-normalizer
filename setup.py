#!/usr/bin/env python
from setuptools import setup

setup(
    name="urlnormalizer",
    version="1.2.1",
    author="Tarashish Mishra",
    author_email="sunu@sunu.in",
    description="Normalize URLs. Mostly useful for deduplicating HTTP URLs.",
    long_description="",
    license="MIT",
    url="https://github.com/alephdata/urlnormalizer",
    packages=['urlnormalizer'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        'six',
        'chardet'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
