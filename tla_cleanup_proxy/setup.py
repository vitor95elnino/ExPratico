#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools

if __name__ == '__main__':
    setuptools.setup(
        include_package_data=True,
        package_data={
            '': ['*.json', 'templates/*.html', 'templates/*.txt'],
        },
        classifiers=[
            'Programming Language :: Python :: 3.8'
        ],
        python_requires='>=3.8',
    )
