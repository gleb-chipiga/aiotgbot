all:
	make isort
	make flake
	make mypy
	make cov
isort:
	isort *.py */*.py
flake:
	flake8 .
mypy:
	mypy .
test:
	python -m pytest tests
cov:
	python -m pytest --cov=telegram --cov-report html tests
clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm .coverage
