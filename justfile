flake8:
    flake8 --exclude .tox .

mypy:
    mypy --strict .

isort:
    isort --skip .mypy_cache --skip .hypothesis --skip .tox .

sort-all:
    -sort-all aiotgbot/*.py

black:
    black --extend-exclude="\.env/|\.tox/" .

coverage:
    COVERAGE_FILE=.coverage/.coverage python -m pytest --cov=aiotgbot \
      --cov-report term --cov-report html:.coverage tests

test:
    python -m pytest tests

all: isort sort-all black flake8 mypy test

build:
    if [ -d dist ]; then rm -rf dist; fi
    python -m build
    rm -rf *.egg-info

upload:
    twine upload dist/*
    rm -rf dist
