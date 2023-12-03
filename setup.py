import re
from pathlib import Path

from setuptools import setup

path = Path(__file__).parent
txt = (path / "aiotgbot" / "__init__.py").read_text("utf-8")
print(txt)
version = re.findall(r"^__version__ = \"([^\"]+)\"\r?$", txt, re.M)[0]
readme = (path / "README.rst").read_text("utf-8")

setup(
    name="aiotgbot",
    version=version,
    description="Asynchronous library for Telegram bot API",
    long_description=readme,
    long_description_content_type="text/x-rst",
    url="https://github.com/gleb-chipiga/aiotgbot",
    license="MIT",
    author="Gleb Chipiga",
    # author_email='',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Internet",
        "Topic :: Communications :: Chat",
        "Framework :: AsyncIO",
    ],
    packages=["aiotgbot"],
    package_data={"aiotgbot": ["py.typed"]},
    python_requires=">=3.11,<3.13",
    install_requires=[
        "aiofreqlimit>=0.0.12",
        "aiohttp>=3.9",
        "aiojobs>=1.2.1",
        "backoff>=2",
        "frozenlist",
        "msgspec",
        "yarl",
    ],
    tests_require=[
        "hypothesis",
        "more-itertools",
        "pytest",
        "pytest-asyncio>=0.19",
        "pytest-cov",
        "sqlalchemy[aiosqlite]",
    ],
    extras_require={
        "sqlite": ["aiosqlite"],
        "passport": ["cryptography<=38"],
        "sqlalchemy": ["sqlalchemy"],
    },
)
