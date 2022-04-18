install:
 	pip install -r requirements.txt
		
test:
	python -m pytest -p no:warnings  -vv testing.py

format:
	black *.py
