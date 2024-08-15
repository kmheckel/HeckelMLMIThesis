# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
long_description = "PwnGym faciliates research on LLMs for computer network operations."


requires = (
    [
        "paramiko",
        "docker",
    ],
)

#extras = {
#    'extras' : [
#        'example_pkg'
#    ]
#}

# This call to setup() does all the work
setup(
    name="pwngym",
    version="0.0.1",
    description="PwnGym: Testing Env for Pentesting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kmheckel/pwngym",
    author="Kade Heckel",
    author_email="example@email.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["pwngym"],
    include_package_data=True,
    install_requires=requires,
    #extras_require=extras
)
