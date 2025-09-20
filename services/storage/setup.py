"""Setup file for storage service package."""

from setuptools import setup, find_packages

setup(
    name="storage",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.103.0",
        "uvicorn[standard]>=0.23.0",
        "sqlalchemy>=2.0.20",
        "alembic>=1.11.3",
        "asyncpg>=0.28.0",
        "pydantic>=2.3.0",
        "pydantic-settings>=2.0.0",
    ]
)