"""
Message Hub Setup
"""

from setuptools import setup, find_packages

setup(
    name="message_hub",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "httpx",
        "structlog",
        "aiosqlite",
        "pytest",
        "pytest-asyncio",
    ],
)
