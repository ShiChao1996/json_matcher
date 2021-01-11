# coding:utf-8
"""
@time: 2021/1/11 6:14 下午
@author: shichao
"""

import setuptools

setuptools.setup(
    name="json_matcher-shichao1996",
    version="0.0.1",
    author="Shichao1996",
    author_email="2483061998@qq.com",
    description="A simple json struct matcher",
    long_description="A json struct matcher, allow you define a template which is expressed in json,"
                     "and check if a json data matches the rule defined by the template. For more, "
                     "it apply a way to get specific data in the template, "
                     "and a way to find if part of a json data matches the template.",
    long_description_content_type="text",
    url="https://github.com/Shichao1996/json_matcher.github.io",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
