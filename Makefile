.PHONY: tests tests-coverage pep8

tests:
	@nosetests ftplugin/mail/*_tests.py

tests-coverage:
	@nosetests \
		--with-coverage \
		--cover-erase \
		--cover-html \
		--cover-html-dir coverage \
		--cover-package vim_mail_refs \
		ftplugin/mail/*_tests.py

pep8:
	@flake8 --ignore=E265 ftplugin/mail/*.py
