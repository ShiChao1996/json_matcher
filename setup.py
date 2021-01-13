# coding:utf-8
"""
@time: 2021/1/11 6:14 下午
@author: shichao
"""

import setuptools

with open("./README.md", "r") as f:
    long_desc = f.read()

setuptools.setup(
    name="JsonMatcher",
    version="0.0.1",
    author="Shichao1996",
    author_email="2483061998@qq.com",
    license='MIT',
    description="A simple json struct matcher",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/Shichao1996",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
