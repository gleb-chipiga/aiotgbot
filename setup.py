import pathlib
import re

from setuptools import setup

root = pathlib.Path(__file__).parent
txt = (root / 'aiotgbot' / '__init__.py').read_text('utf-8')
version = re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]

setup(
    name='aiotgbot',
    version=version,
    # url='',
    license='MIT',
    author='Gleb Chipiga',
    # author_email='',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet',
        'Topic :: Communications :: Chat',
        'Framework :: AsyncIO',
    ],
    packages=['aiotgbot'],
    python_requires='>=3.7',
    install_requires=['aiohttp', 'aiojobs', 'attrs', 'backoff'],
    tests_require=['pytest', 'pytest-asyncio'],
    extras_require={'sqlite': ['aiosqlite']},
    description='Asynchronous library for Telegram bot API'
)
