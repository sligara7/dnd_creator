from setuptools import setup, find_packages

setup(
    name="character-service",
    version="2.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.11.0",
        "psycopg2-binary>=2.9.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "prometheus-client>=0.17.0",
    ],
)
