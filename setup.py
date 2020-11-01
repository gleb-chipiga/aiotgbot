import pathlib
import re

from setuptools import setup  # type: ignore

root = pathlib.Path(__file__).parent
txt = (root / 'aiotgbot' / '__init__.py').read_text('utf-8')
version = re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]

setup(
    name='aiotgbot',
    version=version,
    description='Asynchronous library for Telegram bot API',
    url='https://github.com/gleb-chipiga/aiotgbot',
    license='MIT',
    author='Gleb Chipiga',
    # author_email='',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
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
    package_data={'aiotgbot': ['py.typed']},
    python_requires='>=3.8,<3.10',
    install_requires=['aiohttp', 'aiojobs', 'attrs', 'backoff'],
    tests_require=['pytest', 'pytest-asyncio', 'hypothesis'],
    extras_require={'sqlite': ['aiosqlite']}
)
