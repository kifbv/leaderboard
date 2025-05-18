from setuptools import setup, find_packages

setup(
    name="leaderboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.28.0",
        "aws-lambda-powertools>=2.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "moto>=4.0.0",
            "ruff>=0.0.270",
            "mypy>=1.0.0",
            "aws-sam-cli>=1.96.0",
            "types-boto3>=1.0.0",
        ]
    },
)