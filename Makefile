.PHONY: tests pep8

tests:
	@nosetests ftplugin/mail/*_tests.py

pep8:
	@flake8 ftplugin/mail/*.py
