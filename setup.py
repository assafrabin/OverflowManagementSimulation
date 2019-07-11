import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="overflow_management_simulation",
    version="0.1",
    author="Assaf Rabinowitz",
    author_email="assafrabin@gmail.com",
    description="Simulation for Overflow Management for Multipart Packet",
    license="GNU",
    keywords="simulation",
    url="https://github.com/assafrabin/OverflowManagementSimulation",
    packages=['overflow_management_simulation'],
    long_description=read('README.md'),
    install_requires=['matplotlib']
)
