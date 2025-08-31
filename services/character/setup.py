"""Character Service setup."""

from setuptools import setup, find_packages

setup(
    name="character_service",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
