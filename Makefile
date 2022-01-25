isort:
	isort aaiotgbot tests setup.py

coverage:
	COVERAGE_FILE=.coverage/.coverage python -m pytest --cov=aiotgbot --cov-report term --cov-report html:.coverage tests

build:
	if [ -d dist ]; then rm -rf dist; fi
	python -m build
	rm -rf *.egg-info

upload:
	twine upload dist/*
	rm -rf dist
