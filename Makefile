install:
	pip install -r requirements.txt
test:
	python -m pytest -p no:warnings  -vv tests.py
format:
	black *.py
lint:
	pylint --disable=R,C app.py  tests.py	
all: install test format lint