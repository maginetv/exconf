default: egg

.PHONY: default deb egg clean test install-deps

deb:
	sudo mk-build-deps -i -r
	dpkg-buildpackage -us -uc -b

egg:
	python setup.py sdist

wheel:
	python setup.py sdist bdist_wheel

clean:
	@rm -rf build dist *.egg-info
	@find . -type f -name '*.pyc' -delete

clean-deb:
	dpkg-buildpackage -rfakeroot -Tclean

install:
	pip install -r requirements.txt
	python setup.py install

test:
	PYTHONPATH=exconf nosetests
