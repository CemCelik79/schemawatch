from setuptools import setup, find_packages

setup(
    name="schemawatch",
    version="0.1.0",
    description="Detect breaking OpenAPI changes automatically",
    author="Cem Çelik",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "fastapi",
        "uvicorn",
        "sqlalchemy"
    ],
    entry_points={
        "console_scripts": [
            "schemawatch=schemawatch.cli:main"
        ]
    },
)