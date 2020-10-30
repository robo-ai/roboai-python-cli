
env:
	pip install -r requirements.txt
	
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.ipynb_checkpoints' -exec rm -fr {} +

codequality:
	# ignore E501: line too long
	# ignore W503: line-break before binary operator
	flake8 --count --statistics --ignore=E501,W503

format:
	isort -rc .
	black -l 79 .