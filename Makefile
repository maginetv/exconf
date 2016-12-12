default: egg

.PHONY: default egg clean test install-deps

egg:
	python setup.py sdist

clean:
	@rm -rf build dist exconf.egg-info
	@find . -type f -name '*.pyc' -delete

install-deps:
	pip3 install -r requirements.txt

test:
	PYTHONPATH=exconf nosetests
